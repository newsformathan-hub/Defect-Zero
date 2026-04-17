import streamlit as st
import requests, sqlite3, time
from PIL import Image, ImageDraw
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="DefectZero", page_icon="🔬", layout="wide")

PROJECT     = "pcb-dataset-defect-ddykw"
VERSION     = 2
DB_PATH     = "inspections.db"

CLASS_COLORS = {
    "missing_hole"    : (255, 50,  50),
    "mouse_bite"      : (255, 165,  0),
    "open_circuit"    : (50,  50, 255),
    "short"           : (50, 200,  50),
    "spur"            : (180, 50, 255),
    "spurious_copper" : (0,  220, 220),
}

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS inspections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT, filename TEXT, verdict TEXT,
        defect_count INTEGER, defect_classes TEXT, confidence REAL)""")
    conn.commit(); conn.close()

def save_inspection(filename, verdict, defect_count, defect_classes, confidence):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO inspections VALUES (NULL,?,?,?,?,?,?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
         filename, verdict, defect_count,
         ",".join(defect_classes) if defect_classes else "none", confidence))
    conn.commit(); conn.close()

def call_roboflow(img_bytes, api_key, conf=35):
    url = f"https://detect.roboflow.com/{PROJECT}/{VERSION}"
    resp = requests.post(url,
        params={"api_key": api_key, "confidence": conf},
        files={"file": img_bytes}, timeout=30)
    return resp.json() if resp.status_code == 200 else None

def draw_boxes(img_pil, data, orig_w, orig_h):
    img  = img_pil.copy().convert("RGB")
    draw = ImageDraw.Draw(img)
    api_w = data.get("image", {}).get("width",  orig_w)
    api_h = data.get("image", {}).get("height", orig_h)
    sx, sy = orig_w / api_w, orig_h / api_h
    for p in data.get("predictions", []):
        cls   = p["class"]
        conf  = p["confidence"]
        x  = (p["x"] - p["width"] /2) * sx
        y  = (p["y"] - p["height"]/2) * sy
        x2 = (p["x"] + p["width"] /2) * sx
        y2 = (p["y"] + p["height"]/2) * sy
        color = CLASS_COLORS.get(cls, (255, 255, 0))
        draw.rectangle([x, y, x2, y2], outline=color, width=3)
        label = f"{cls} {conf:.2f}"
        draw.rectangle([x, y-22, x + len(label)*8, y], fill=color)
        draw.text((x+3, y-19), label, fill="white")
    return img

init_db()

st.title("🔬 DefectZero — PCB Defect Detection")
st.caption("Powered by YOLOv8 + Roboflow | 6 defect classes")

tab1, tab2, tab3 = st.tabs(["🔍 Live Inspection", "📊 Inspection History", "📥 Export Reports"])

with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        api_key  = st.text_input("Roboflow API Key", type="password")
        conf_val = st.slider("Confidence Threshold", 10, 80, 35)
        uploaded = st.file_uploader("Upload PCB Image", type=["jpg","jpeg","png"])

    with col2:
        if uploaded and api_key:
            img_bytes      = uploaded.read()
            img_pil        = Image.open(io.BytesIO(img_bytes))
            orig_w, orig_h = img_pil.size

            with st.spinner("Running inference..."):
                t0      = time.time()
                data    = call_roboflow(img_bytes, api_key, conf_val)
                elapsed = time.time() - t0

            if data is None:
                st.error("API call failed. Check your API key.")
            else:
                preds        = data.get("predictions", [])
                defect_preds = [p for p in preds if p["class"] != "good"]

                if not defect_preds:
                    verdict = "PASS"
                    st.success("## ✅ PASS")
                elif max(p["confidence"] for p in defect_preds) >= 0.70:
                    verdict = "FAIL"
                    st.error("## ❌ FAIL")
                else:
                    verdict = "REVIEW"
                    st.warning("## ⚠️ REVIEW")

                st.caption(f"Inference: {elapsed:.2f}s | Detections: {len(defect_preds)}")
                annotated = draw_boxes(img_pil, data, orig_w, orig_h)
                st.image(annotated, caption="Annotated Result", use_column_width=True)

                if defect_preds:
                    st.dataframe(pd.DataFrame([{
                        "Class"     : p["class"],
                        "Confidence": f"{p['confidence']:.2f}",
                        "X": int(p["x"]), "Y": int(p["y"])
                    } for p in defect_preds]), use_container_width=True)

                classes  = list(set(p["class"] for p in defect_preds))
                avg_conf = round(sum(p["confidence"] for p in defect_preds)/len(defect_preds), 3) if defect_preds else 0.0
                save_inspection(uploaded.name, verdict, len(defect_preds), classes, avg_conf)

        elif uploaded and not api_key:
            st.warning("Enter your Roboflow API key above.")
        else:
            st.info("Upload a PCB image to begin inspection.")

with tab2:
    conn = sqlite3.connect(DB_PATH)
    df   = pd.read_sql("SELECT * FROM inspections ORDER BY id DESC", conn)
    conn.close()

    if df.empty:
        st.info("No inspections yet.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Inspections", len(df))
        c2.metric("Defects Found",     len(df[df["verdict"]=="FAIL"]))
        c3.metric("Pass Rate",         f"{100*len(df[df['verdict']=='PASS'])/len(df):.1f}%")
        st.bar_chart(df["verdict"].value_counts())
        st.dataframe(df, use_container_width=True)

with tab3:
    conn = sqlite3.connect(DB_PATH)
    df   = pd.read_sql("SELECT * FROM inspections ORDER BY id DESC", conn)
    conn.close()

    if not df.empty:
        csv = df.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, "inspections.csv", "text/csv")
    else:
        st.info("No data to export yet.")
