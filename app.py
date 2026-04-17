
import streamlit as st
import requests, os, cv2, sqlite3, time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="DefectZero", page_icon="🔬", layout="wide")

RF_API_KEY  = st.secrets.get("RF_API_KEY", "")
PROJECT     = "pcb-dataset-defect-ddykw"
VERSION     = 2
DB_PATH     = "inspections.db"

CLASS_COLORS = {
    "missing_hole"    : (255, 50,  50),
    "mouse_bite"      : (255, 165,  0),
    "open_circuit"    : (50,  50, 255),
    "short"           : (50, 200,  50),
    "spur"            : (180,  50, 255),
    "spurious_copper" : (0,   220, 220),
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

def draw_boxes(img_pil, predictions, orig_w, orig_h):
    img = img_pil.copy().convert("RGB")
    draw = ImageDraw.Draw(img)
    scale_x = orig_w / predictions.get("image", {}).get("width", orig_w)
    scale_y = orig_h / predictions.get("image", {}).get("height", orig_h)
    for p in predictions.get("predictions", []):
        cls   = p["class"]
        conf  = p["confidence"]
        x     = (p["x"] - p["width"]/2)  * scale_x
        y     = (p["y"] - p["height"]/2) * scale_y
        x2    = (p["x"] + p["width"]/2)  * scale_x
        y2    = (p["y"] + p["height"]/2) * scale_y
        color = CLASS_COLORS.get(cls, (255, 255, 0))
        draw.rectangle([x, y, x2, y2], outline=color, width=3)
        draw.rectangle([x, y-20, x+len(cls)*8+50, y], fill=color)
        draw.text((x+3, y-18), f"{cls} {conf:.2f}", fill="white")
    return img

init_db()

st.title("🔬 DefectZero — PCB Defect Detection")
st.caption("Powered by YOLOv8 + Roboflow | 6 defect classes")

tab1, tab2, tab3 = st.tabs(["🔍 Live Inspection", "📊 History", "📥 Export"])

with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        api_key = st.text_input("Roboflow API Key", value=RF_API_KEY, type="password")
        conf    = st.slider("Confidence Threshold", 10, 80, 35)
        uploaded = st.file_uploader("Upload PCB Image", type=["jpg","jpeg","png"])
    
    with col2:
        if uploaded and api_key:
            img_bytes = uploaded.read()
            img_pil   = Image.open(io.BytesIO(img_bytes))
            orig_w, orig_h = img_pil.size
            
            with st.spinner("Running inference..."):
                t0   = time.time()
                data = call_roboflow(img_bytes, api_key, conf)
                elapsed = time.time() - t0
            
            if data is None:
                st.error("API call failed. Check your API key.")
            else:
                preds = data.get("predictions", [])
                defect_preds = [p for p in preds if p["class"] != "good"]
                
                if not defect_preds:
                    verdict = "PASS ✅"
                    st.success(f"## {verdict}")
                elif max(p["confidence"] for p in defect_preds) >= 0.70:
                    verdict = "FAIL ❌"
                    st.error(f"## {verdict}")
                else:
                    verdict = "REVIEW ⚠️"
                    st.warning(f"## {verdict}")
                
                st.caption(f"Inference: {elapsed:.2f}s | Detections: {len(defect_preds)}")
                
                # Draw and show annotated image
                annotated = draw_boxes(img_pil, data, orig_w, orig_h)
                st.image(annotated, caption="Annotated Result", use_column_width=True)
                
                # Show detection table
                if defect_preds:
                    rows = [{"Class": p["class"], "Confidence": f"{p['confidence']:.2f}",
                             "X": int(p["x"]), "Y": int(p["y"])} for p in defect_preds]
                    st.dataframe(pd.DataFrame(rows), use_container_width=True)
                
                # Save to DB
                classes = list(set(p["class"] for p in defect_preds))
                avg_conf = round(sum(p["confidence"] for p in defect_preds)/len(defect_preds), 3) if defect_preds else 0.0
                save_inspection(uploaded.name, verdict.split()[0], len(defect_preds), classes, avg_conf)
        
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
        c2.metric("Defects Found", len(df[df["verdict"]=="FAIL"]))
        c3.metric("Pass Rate", f"{100*len(df[df['verdict']=='PASS'])/len(df):.1f}%")
        
        verdict_counts = df["verdict"].value_counts()
        st.bar_chart(verdict_counts)
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
