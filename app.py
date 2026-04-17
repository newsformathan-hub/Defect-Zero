import streamlit as st
import requests, sqlite3, time
from PIL import Image, ImageDraw
import pandas as pd
from datetime import datetime
import io, base64
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

st.set_page_config(page_title="SolderSense AI | Data Patterns", page_icon="\U0001f52c", layout="wide")

DP_LOGO_B64 = "iVBORw0KGgoAAAANSUhEUgAAAN0AAABECAYAAAAFrTCRAAAACXBIWXMAAAsTAAALEwEAmpwYAAAKT2lDQ1BQaG90b3Nob3AgSUNDIHByb2ZpbGUAAHjanVNnVFPpFj333vRCS4iAlEtvUhUIIFJCi4AUkSYqIQkQSoghodkVUcERRUUEG8igiAOOjoCMFVEsDIoK2AfkIaKOg6OIisr74Xuja9a89+bN/rXXPues852zzwfACAyWSDNRNYAMqUIeEeCDx8TG4eQuQIEKJHAAEAizZCFz/SMBAPh+PDwrIsAHvgABeNMLCADATZvAMByH/w/qQplcAYCEAcB0kThLCIAUAEB6jkKmAEBGAYCdmCZTAKAEAGDLY2LjAFAtAGAnf+bTAICd+Jl7AQBblCEVAaCRACATZYhEAGg7AKzPVopFAFgwABRmS8Q5ANgtADBJV2ZIALC3AMDOEAuyAAgMADBRiIUpAAR7AGDIIyN4AISZABRG8lc88SuuEOcqAAB4mbI8uSQ5RYFbCC1xB1dXLh4ozkkXKxQ2YQJhmkAuwnmZGTKBNA/g88wAAKCRFRHgg/P9eM4Ors7ONo62Dl8t6r8G/yJiYuP+5c+rcEAAAOF0ftH+LC+zGoA7BoBt/qIl7gRoXgugdfeLZrIPQLUAoOnaV/Nw+H48PEWhkLnZ2eXk5NhKxEJbYcpXff5nwl/AV/1s+X48/Pf14L7iJIEyXYFHBPjgwsz0TKUcz5IJhGLc5o9H/LcL//wd0yLESWK5WCoU41EScY5EmozzMqUiiUKSKcUl0v9k4t8s+wM+3zUAsGo+AXuRLahdYwP2SycQWHTA4vcAAPK7b8HUKAgDgGiD4c93/+8//UegJQCAZkmScQAAXkQkLlTKsz/HCAAARKCBKrBBG/TBGCzABhzBBdzBC/xgNoRCJMTCQhBCCmSAHHJgKayCQiiGzbAdKmAv1EAdNMBRaIaTcA4uwlW4Dj1wD/phCJ7BKLyBCQRByAgTYSHaiAFiilgjjggXmYX4IcFIBBKLJCDJiBRRIkuRNUgxUopUIFVIHfI9cgI5h1xGupE7yAAygvyGvEcxlIGyUT3UDLVDuag3GoRGogvQZHQxmo8WoJvQcrQaPYw2oefQq2gP2o8+Q8cwwOgYBzPEbDAuxsNCsTgsCZNjy7EirAyrxhqwVqwDu4n1Y8+xdwQSgUXACTYEd0IgYR5BSFhMWE7YSKggHCQ0EdoJNwkDhFHCJyKTqEu0JroR+cQYYjIxh1hILCPWEo8TLxB7iEPENyQSiUMyJ7mQAkmxpFTSEtJG0m5SI+ksqZs0SBojk8naZGuyBzmULCAryIXkneTD5DPkG+Qh8lsKnWJAcaT4U+IoUspqShnlEOU05QZlmDJBVaOaUt2ooVQRNY9aQq2htlKvUYeoEzR1mjnNgxZJS6WtopXTGmgXaPdpr+h0uhHdlR5Ol9BX0svpR+iX6AP0dwwNhhWDx4hnKBmbGAcYZxl3GK+YTKYZ04sZx1QwNzHrmOeZD5lvVVgqtip8FZHKCpVKlSaVGyovVKmqpqreqgtV81XLVI+pXlN9rkZVM1PjqQnUlqtVqp1Q61MbU2epO6iHqmeob1Q/pH5Z/YkGWcNMw09DpFGgsV/jvMYgC2MZs3gsIWsNq4Z1gTXEJrHN2Xx2KruY/R27iz2qqaE5QzNKM1ezUvOUZj8H45hx+Jx0TgnnKKeX836K3hTvKeIpG6Y0TLkxZVxrqpaXllirSKtRq0frvTau7aedpr1Fu1n7gQ5Bx0onXCdHZ4/OBZ3nU9lT3acKpxZNPTr1ri6qa6UbobtEd79up+6Ynr5egJ5Mb6feeb3n+hx9L/1U/W36p/VHDFgGswwkBtsMzhg8xTVxbzwdL8fb8VFDXcNAQ6VhlWGX4YSRudE8o9VGjUYPjGnGXOMk423GbcajJgYmISZLTepN7ppSTbmmKaY7TDtMx83MzaLN1pk1mz0x1zLnm+eb15vft2BaeFostqi2uGVJsuRaplnutrxuhVo5WaVYVVpds0atna0l1rutu6cRp7lOk06rntZnw7Dxtsm2qbcZsOXYBtuutm22fWFnYhdnt8Wuw+6TvZN9un2N/T0HDYfZDqsdWh1+c7RyFDpWOt6azpzuP33F9JbpL2dYzxDP2DPjthPLKcRpnVOb00dnF2e5c4PziIuJS4LLLpc+Lpsbxt3IveRKdPVxXeF60vWdm7Obwu2o26/uNu5p7ofcn8w0nymeWTNz0MPIQ+BR5dE/C5+VMGvfrH5PQ0+BZ7XnIy9jL5FXrdewt6V3qvdh7xc+9j5yn+M+4zw33jLeWV/MN8C3yLfLT8Nvnl+F30N/I/9k/3r/0QCngCUBZwOJgUGBWwL7+Hp8Ib+OPzrbZfay2e1BjKC5QRVBj4KtguXBrSFoyOyQrSH355jOkc5pDoVQfujW0Adh5mGLw34MJ4WHhVeGP45wiFga0TGXNXfR3ENz30T6RJZE3ptnMU85ry1KNSo+qi5qPNo3ujS6P8YuZlnM1VidWElsSxw5LiquNm5svt/87fOH4p3iC+N7F5gvyF1weaHOwvSFpxapLhIsOpZATIhOOJTwQRAqqBaMJfITdyWOCnnCHcJnIi/RNtGI2ENcKh5O8kgqTXqS7JG8NXkkxTOlLOW5hCepkLxMDUzdmzqeFpp2IG0yPTq9MYOSkZBxQqohTZO2Z+pn5mZ2y6xlhbL+xW6Lty8elQfJa7OQrAVZLQq2QqboVFoo1yoHsmdlV2a/zYnKOZarnivN7cyzytuQN5zvn//tEsIS4ZK2pYZLVy0dWOa9rGo5sjxxedsK4xUFK4ZWBqw8uIq2Km3VT6vtV5eufr0mek1rgV7ByoLBtQFr6wtVCuWFfevc1+1dT1gvWd+1YfqGnRs+FYmKrhTbF5cVf9go3HjlG4dvyr+Z3JS0qavEuWTPZtJm6ebeLZ5bDpaql+aXDm4N2dq0Dd9WtO319kXbL5fNKNu7g7ZDuaO/PLi8ZafJzs07P1SkVPRU+lQ27tLdtWHX+G7R7ht7vPY07NXbW7z3/T7JvttVAVVN1WbVZftJ+7P3P66Jqun4lvttXa1ObXHtxwPSA/0HIw6217nU1R3SPVRSj9Yr60cOxx++/p3vdy0NNg1VjZzG4iNwRHnk6fcJ3/ceDTradox7rOEH0x92HWcdL2pCmvKaRptTmvtbYlu6T8w+0dbq3nr8R9sfD5w0PFl5SvNUyWna6YLTk2fyz4ydlZ19fi753GDborZ752PO32oPb++6EHTh0kX/i+c7vDvOXPK4dPKy2+UTV7hXmq86X23qdOo8/pPTT8e7nLuarrlca7nuer21e2b36RueN87d9L158Rb/1tWeOT3dvfN6b/fF9/XfFt1+cif9zsu72Xcn7q28T7xf9EDtQdlD3YfVP1v+3Njv3H9qwHeg89HcR/cGhYPP/pH1jw9DBY+Zj8uGDYbrnjg+OTniP3L96fynQ89kzyaeF/6i/suuFxYvfvjV69fO0ZjRoZfyl5O/bXyl/erA6xmv28bCxh6+yXgzMV70VvvtwXfcdx3vo98PT+R8IH8o/2j5sfVT0Kf7kxmTk/8EA5jz/GMzLdsAAAAgY0hSTQAAeiUAAICDAAD5/wAAgOkAAHUwAADqYAAAOpgAABdvkl/FRgAARjxJREFUeNrsnXe8XlWV979773POU27PzU1CSO8JKSShRwSCUqUIBOyOAurYG77jqzPjjDo6jmV0LEOxggVxQEaUEaRLJyQhhZSb3m5uya1PO2Xv949znnLu8zwRnEic1zl+Isk+z1l7rbXb2r+19trCGPMgMIVj8Hz+85/nnHPO4YwzzoiVb1y/gc5t27jsitfHynO5HJ///Of50Ic+REdHR6ncGMPtt9/OrFmzOOmkk2LfPP744+zfv5+rr746Vt7b28udd97Jddddh5QypAMI4Iv/9AUuvOhClpx4Yuyb1atXs3//fi699NJYeVdXF/feey/veMc7qmT89je/xaprrqajo6NEH+BHP/oRjuNwzTXXIIQovTt44CD33/db3vZXf1VF67Of/SyrVq1i3rx5Mdlvu+02TjjhBJYtWxb7/bNPP8NDDzzAJ/7vJ2Plvu/zrW99i7e+9a2MGTMm9u6WG29i8qTJnH/xhbHyPXv2sHXrVl7zmtfEyg8ePMjXv/51PvOZz5BMJmPvfnDLTSxbfjKLly7FRAIK4OEHH2L9hvW8/wMfQAgRa98f/OAHXH/99ViWVZIP4N++8jUuuvQSZs2ZHavj7rvv4vDhw7zjHddWtCDs27uX7950M5/6u7/Dsq3Sm8AP+Jd//mfe/La3Mnny5GPR7fdYwDzguGNRe2dnJ0uXLq0qHxkeZt/efVXlWmvWrVtHEASxciEE+/fvjw3E4tPf38++fdW0PM9j586dpQFX+WzYsIHTTjutJq1Dhw5Vlbuuy/bt22vKuGXzZjzPqyrfvn07TU1NsU4X0iqwe/eemrTWr1/PBRdcUCX7nj17mDhxYtXve3t72bhxU1W5EIJt27bh+341X52dKKWqynO5HF1dXVXlhUKBNWvWlAbH6PadPSeaICrE7O7uprOzs0p23/fZunVrnJYAgWDTpk28euU5VXXs3r27ZptkM1k2bNhQ1b7KUmzevJlcNssxetISOGa1JxKJ0oxW+di2g+3YNb9xHKfmQLFtu2ZnsSyrZh1KKWzbrstXLVpSyrq0HMepzW8iUZPfRCJRs355BFr19JWoU4dSikTCqctvPT3WqkMIUVf20StciZbjxL4xFXUkEomadYyWXUSjtV6b1NNjkdbogX0kWq/Qk5Uc88dU/NdEfwsqyisVWf5Tm46pXS5q/ab67wYdVWQwL6OOkB9TW7yKdyH92vWLir+berSOJGOtckFJDo2uoGvq6kJj0C+nDgzG6FKbVP/KRKxUyChMDV7Kf6/VvloYEOal9yphMNE3YcuW5Teibmu9Io91rAecUpLR9oeQAllD85alkALsGjOulKKCVuVMLFFSVNVhWZLyRB+Wy+J/BXVpSSlqrA5WzXIAJQWWJSP6MsavrMOXqENL1OFLylA3tVYhGRVX1g0CEfumQvdK1KxfKYlUtcuFKNMSMdkVsqJ9RWk1r9Z9qX1l7RXVKCpoxa2P8ootYrKHE3T4TlW8q6Pev4xBpwNNT3c33d3dGO2Hm12h6D50iMHBQboPdZfseyEM2WyGfD7PgQMHcF2//E4KhgcH6evtpbv7EEaXO2lvTw/DQ4N0HzqEMUFxVNPdfYjMSIZDXQcxGARghEAiKWRzHO7uHVU/HO7tY2hgIOK3XH7w4AEyw8NRHRqiDi4EZIeGObj/AEEQrQiRjCNDQwR+EONLCMWhrkNkRoq0TMxcKuRy9Pb0xPmSguGh4VD2Q4cofiKEoK+nl/xIjkNRHSJiSgcBuUyWroMHKRRcigoTQpHLZBiq0j30dHczeHigqo5DXV34rsuB/ftJJFOxdyMjGXp6wjbROijJ3tfbS2YkU9UmmZFhMsPD7N+7D8t2KiwVQT6bC/vK2Mr6YWhgkGyJVgiXCCHo6erGyxU4uH8f0lIYYxDROzeXrzmpv1KPMMZ0AjOPReXvftf17OzsZPKUKWAMWoSG1vBAP4P9g0ybPqPU8EaAH3isWbOGRQsXkUqmKWpfSsGOHSEwMbZjXMWAEBw6dJBsNsv0GTMwOupcUpLP5di9ezdz5s4FExkeIpyN1z+/lklTpjBm7NhyxxeG3p5estksU6dOLTU8QpDPZdm7dw+z58yJ7BZRovXihg1MnzkDJ5UMTScTzr6dnduQUjJj5ky01qUBkctmObD/ALPmzC7xW7S31qxezYyZs2htayvJKKVg27attLa20j52bMmeFELQc6ibA/v2smjZiRgRWmcCgdaazZs3M2vWTJxEoqRHISSbN79IQ0Mjk6dMLetLQCYzQn9/P5MmT4nGqEFIQTaTYcOG9SxbthylrKKBjhCCrS9uomN8B63t7WCKsgsOHjjAQP8ACxaeEMkRDhbf99i2bRtz585HKgUVut+wfj1TpkyluaWlZBsKKdi1cweFQoG5c+fFB/zwMJ1bNrN46VJQsjSxEhh2bOvktl/cwaRJk45Ft9+OMabTHKPnXe96l/nNr39tfN+P/Xn2qafNd775rfDfXvTH983Q0JC54oorzMGDB6ve/evXvmZ+97vfVZXfc8895l+/9rWqOg4cOGA+/alPVZX7vm+ufftfmYcffKiK1v333WduueWWqvK9e/aYz3zmM2UaXpnWxz/8UbN/7z7j+77xoj++75t/+uznzNe++tXS77zom53bt5svfvYfo3Iv+hO+e/Ob32yee/bZqvq/9M9fqin7vff8xlz3V+8o11H8r+uZj3zoQ+bQoa4q2T/9N580P/ju96povbhpk/nxj39cJeOunTvNJZdcYoaHh6to/f2nPmme+P0jpbrdqPyO239uPv7Rj1X8NpRxYOCwueGGj5lcLlelxw+8+6/N2ufXVPH1nW9/0/zd3326TKfE70bzxlVXGc/1YrL7vm+uf8c7zbZt245Vt+88xns6UJZVhSQppUp/YrawbZdQtNHvZJ1vwn1NDVqWVbO8uBLWpBXVW6tcRt/UQzxHvxNSImryZSOVrM9XTdnr8atKssRfhHzVpPVHyC6EwKqBHo+mVfSVKaVq6suyQz3aL4FWZbvXpFXiy6qpx2P5HNPaRR272hhT0+9TNHdqvqv3zcssj14ePVoYdJHvSpzOmLL5WAF+Hm2+qCgv1a3NUdNXyfyvlKXGN6NRTTPqX3G+9B/Jl6nBl6EWtnwssZRju9KZSqg81k3ruwxiLoBKJdaGmuvD+aY+zP8yIfsjugwq+BXx3XScX1GmZepMRjHYfVQd9WSvLC9hpZJSdEhNqL2WjEeou279IXRSqltU0jLVQ0AcEdyoo/s49lqnbUbr/ti6DOSxHXOmJtQtlUTVMAEsK4SB7ZrwuKxJy7JUTZj9SDB/CFsfPVq2U8PEUbVdHLZjIZRVh1Y910A9fuvxFboF7Jqml6gJzdt2HdktC4GpSUtKhaohi2XJOi4hq24AgqjTJkVTtZpWuBWpNRsIxTF9jil6ef3117Nr53amTJmKMTpyGQiG+gcYHBhkyowZJdNMCEMQ+Dy/+nkWL1mC4yRLJoSK0MuWlhba29sJSqCfpLuni8zICDNmzCyZLUIICoUCO3bsYN68eWHsYxEJFYIX1qzl+Mlx9FII6OnpJpfLMmXKNHQFQloohEjo3LlzI2uuPHNv2bCe6bNn4SQS5TqkZMvWLSipmDVrVhm9RJDP59i7bx+zZs2J1S0FrFmzhpkzZ9LU3FKqX0rB9u2dtLS0MHZsRxnBk5Keri66Duxn8dKl6ArZIQx1mzt3LrZtR3B6+M2LmzaSbmiMZNSlOjIjwwwODnL88ZMIKmTP57JsWP8Cy086CSkVuqL+zk2bGDdhPC1jxpR0L6Xk0L4DHO4fYMHChWgdOa0FBIHPli1bmDdvAVLKkC8hEMKwce06pkyfRmNza4UeBbt37SSfzzNv/ny0NhhTRi+3b9nM0pNPRptoNY6Q287Obfz0Zz8/VrGX24+5ebnq6qs588xXY3Q46KSUbFq/nk2bXuSqa66pGHSCfC7Dpz79ad7z7vfQPrYj1ol/8uNbmTN7DiedckpFh5Q8+ugj7N27hze/+a1oHZQGY19fDz/72c943/veH+4wDCVn6mc+/Wkuvexylp18cqzjPf30Uxw4sJ/Xv/6qGF/d3V3ceeedvOc9761wMYTG1b9++V94y9vfHroyoo6nlOLGG/+dVCrFW9/69pIPCyHp6jrAr++5h2uve1d50EX1fOpTn+SNb3wT8xYsqHAZSL73vVtYtGgRJ58cl/3xxx7jd/f9lhtu+ATaBCUZjTF85Stf4dprr6WtbUxp0Eml+LdvfJ3Jkydz2eVXxGTftXMnW7Zs5vwLLoxNOF0HD/DFL36BD3/4wziJVKxN/v2b3+T0FaezZOmyEi0lFQ/c91vWvbCBj378Y+ggmmxl6Ja4+eabed/73o9l2aW9n5KSf/7c57li1VXMmjM3VscdP/8ZfX19/PVfv49AByU/3e5du7jpO9/mox/9CEJWuh8En//cZ/F97y9zT6csi9mz5jB//oJYuV/wGBgYYv78+fFy36epsZnFS5bQ0tIaezdxwvHMnDGritb+ffsJvKCK1sBAPw8++BALFpxQxVdr6xhmzppd9U1vbx9K2VXl48aN4/HHn2TBggVVtNraO1i4aBFjxrTHyo8bP5F0Y0MVrfa2NtY8+2xNWk3NrcyZO48Fo2ScOHESM2fOrpL94P79tLa2Mm9UHWE97SxatJjm5pa4LO3jmDp5WhVfyWSKTDZXVUd7ezvphiYWLT6xCkHs6GhnzpxqvrZt3cbeAwer+HLdPO1jx7BkyYnVemwdw5w585i3IP7N8ZMmIaSsopVOpWhsbOSEhYuraDU3tqAD/Ze5pwPwakS6e55XdZIgbBQXbQyuWz1LBUGA71XT8n2/RMvEaHkEdRSvta55MsDzvJqR+a7r1uS3SKvIb2VEaRAE8W9MJV/By+IrCIKa5b7vlVaY0eil1hq3Di2/TpvUk90Yg+u6R+TLQMlx7vt+jK9Y++oAz3dfsuyV7VvZwp7nhqZrDfSyVt1/MYPulRA+RDWPDkD8h2Dzem4RcQR6f5bPMeXL/OnhfHFsgy+P7Z5OSqjhBDZSomuhTlKFTVIDrTJSolWdcimqYWMpCeqwFQiBqVGHUCrC26vlqAfz6wpasoIHIyW6GjUHpfDrzIWmqLPRddTViSKo4LfEoYx4kqomv7qW81iqmjpBSrQJ94NVtKTCROilGCW7EbXrQNhQA/HUUoT6rwVFiuqAZ5RCS1UK3hZ12uSYDLrcSAaMRoni8ZZXZhZQykZ4efzMMH4uRxB40WbewhsZJMhnCHI5/MCL+onEzYxgaw9veBAvnYzscoOlHLSbxc+P4OeyBIFfqsPPjqDzGYJcHj9wSxvw/GA/ws3jZUZK6BZCoKQFQQEvW+YLwFI2JptBuLk4X1LhjgyFsuSy4WY+CryVUmC8HIXhQbzGhhKQYykHXcggFKP4UniZIfALMTkEAikVlu8SZIZj7yxlg5uN6bEoe5AbQQUeQVReBFaNNgjfxR0exHXsUiC2Ug7CL2AKWYJcHi9wSwBLkB2GQjYuu1J4w4PY2sMdGkCm0iWUVCkbfBc/mw350j4Yg6Vs/NwIePlYHUJICiPDCM8jN9AfnquLnPtK2Ujt4o0MVcluclmk68b0qJSFOzyErf2wbSJ02giBFBLh5/Gzw3jZTKlN/vQLeHjOIxAgHnnzVZ2D+w/OTEiBloY6B8n+BCu8pK+vl3Q6TSqVDhvehJB9wXUpFAo0NTeXoe5oL9LX18eYMWNKkePFATk4PIRj2ySTqTI8LSSZXBbf82hpbonB5kEQMDw8TGtr66ho/pCvhoaGGC2FJJfP4vsBTU1NBBW0fD9gJDNCa0tLlck4MDBAU1Mz1ih+BwYHEELQ0tJagaoKfN8nk8nQUkFLRAOvr7eXpuZm7IRTRctJJEhV8CuEJJfLkstkGds+FmM0WpRN3v7+fpqbm0s+rlD3koHBfpRl0djYFNOX53m4rktjY2MMuQ08n/7+fsa2t4craGkxlfQP9JNKpUgkkvE2yWYoFAqMaRtTqqNobg8ODdHS3BzbEigEh/sP09jYiOXEZR8eGkLrgNaWtujMXJnfoYFBxo5tB1M+QyeEoK+vj5aWFizLegVNfInS4Eu2i3vPPaVzeMfemUkp8F/JFdeEsXY60GEjlqLgo32QlPhBUI7UiN5ZloUf+HHTzIQwvDE6hLNFuVwqGXYOP4jZGKUZfDRoUeIriFbASGUmipcUEOj4Mc+6tAArKjej+bUUmNA3VbnHEITO6UpaIpLfsqwQgKmkFtEyWsf4DXUiUUKWABAt6vNV1K9SCm0MQdQmsb2pEKF1ISq7Uui09r3waJap0L1lKbSu3SYymqxGG1aWUmG715G98iiuiNpdRKBN5eFUIQS2VCXZK99ZlkXgB0c4LPwnWGRMedBZSqVxlI1xFJa2whO6/23wIqbjuqLpcBqr2loUv6lldvsAllO16zEV24JaeyFp1ym3jsAXtfkSsjrg6Ei0hFX79+FWLPGS+fKjXXhN2evw6wNEZ9PkS+ArOIIea20pRURL2k7tPaiqTUvXaRP9B2QXo/dnFZDg6HeVsle+qyf7n3bUaYQRCKGwSqkKRDG27s8UUfvf53+f/9FPOShb/q8yXrGp7hX9WvxZdrijN6WLo8mXeWW1Zf0pFGBMFMsoXDA2yoAxCt+K0CUtEUg0gkCBYzw08ohzgDLgS0onvPEDrMAjsG2MVKhiaJKRBFIgtI8VaLQICKINvjSE74rmho7SAImySwIkViDwlEEag5EG29MYowmUwEgLOxAEkpodKXZwwICWoEyAj4/SikAoNAZhBMoYBKEuXEsABlsbfAVSV3RUAZ4UOL5G+uHeCUvhKomlxahOHSCMIS8FSgssU97riOLeNDoz4EuNMFaUpsILoxNLJ/UFxVxAooJ6+F5ihEILhZEGNFjGQ2lJIAxagqWhIAWB0EjtYIswM4CtfVypsQJVak9pJJKwPiMMnh1gBRZSSwIVmmXgI5H4JtyLeUqS1BaiCJ7UaAsjQBqDJwy2L9AWYX+kgC8Vtp8AmSdvFVB5hadDgzyFjbQEruUgjag0Yv98Bl1lZxOAloac5ZDUGqVtXCcAo3ACO3xvRUhpziU5mCWfEFh2W3SsJag7J+lotNiuj06k8Bsn4BzuRWifoLjZEBBYOTAWRqURooCnBBqwNVgRp8VBqLSJIGXIyQBbi1K+FC00CU+TaWjApJsgmyGRHcGzws5u6szelbrwlCFZMAQqTeAYlHBJ+RaBsPCUICDANwXUsIfCotDoYBkTG75GBFhGoLViqH0M2nJo7usjoQOCmPcPhGVha4VjVBgkrvzSJJMXBj9EqlBGkNIaY8AnQEobTDnprpZF/YCnQqg7PIqlCYSDNB5C53C0RcFpIjCAtvClwZfgG2jwwEhNQaZJeMMMO5q0b8jbaQLbxTEaK7DwpQr9g9rFNy5qyODZBXSDTcJPYBAooTFaYByHJs+QNS4EeSyZCIedqB4anoS0byhYSYSvSARZXBH2PS0MWdslOewim9JYM6aQ7hiPkprMwS5GuruwMkM0yQR52ypNRn9Wg660sfU81OQpnPmVr6PSCfxAkJIS0kmUUfjCIIxG5j0KmSH6tm/l0N330P3sI9gBKCtZ03bwVLQ6+YacLTjlm19k7MIzWf+Db9L19W9hNTRGKKOBQZdpb3sLk//qelTglbI/ad8nMEXoWKJsq3RGzM/neeKGjyC2bqWQdJBGAhrXVSz9ymdpW3E2wy+s4YW/fj/aZDHYL0kfdgDDvmbOhz7AxPPOQ3ouxljoBhsbB+3nCYaH6d/+Itvu/iX6oadJpBRuxTEWLQzpbIHhKbO44KYbcVraePIj70c++ntyTenSClUINIs++TnGrzgdAoOngvDcmu9H+UE0UllI2wLjg7TZc99v2HrrHZz5na9jNTSWJhDt+qXcMUIYHGmDEPjCoKXFtltupuv7NyFOPpUVX/oKIkodaCGQlgVC4IkAoQ3Sl6z72IcRm58n0zSGZV/+Mk3TpiNdg5E2ukGGTm7XRQxn6d+5i85f/IiRx38PKQsjDcI3+EKw7B+/QOOCReSHunjqE3+Hv6eTtJ1Em3jaRIEg6QeMGJ8Ff/8JjptzIk/c8EHcnbtJCpsGNyDj5Wh6y9tY+MZraZs9AyvKtZrPFxjYvYfdv7iNPT/6IY7WRzWK5ehHpBhDg5C0LVhIKuHgAtmhIUZWPw+2ACVwGhqwjjuecXNn075sOdNWXc3+X9zOlq9/A7/rAKIGEqYipDrv5eg442wmvfpiFIop519Ez423YoyHEIpAGHytSXaMZcyM6eRGRjBRbGRjRwdFrDDIFsj3D6JSCVQ6CbaEZBqhNb6EpCcQhTzylNOZfN5FaCdJw5lnsnb2NBJr1+E32FVoWT0bQOuAxPRJjJk1hwAI8i5777kTrQM6TjuV1hOX0XziMmZcfBlPf/GLHPzpT3C0wRSjKYzFiO8y9bILGTt7PgZoWXEyhx7+fdSEoYlltKFpyiQapk/D9I/gBjmksEmNHUMAeICbzSAyWZK2hWpuoaFjPMpA45w5WChMtoDveqQmtaKic4AFIN/XB0LgJB2a0o3sGduGH/gknCRj5s3HjpDPjJtF9w5gK4VlJ7BTaSxboaQDgY0RFg3z59N6/AwARg4cpOfB+3Ha22g58UQaZsylYclSpp51No/+7d/T99s7SSSsyFSXpGfPo232bASzOe3/3MADf/Mh5IhLQtlFb24FYGEwgSE1awGti04k4TTgaR9tOQx7BY6/+h2c+tnPUkCy6Y6f0fXww4hGhwVXvJnjTjsd7+yVdN52K4mjHDRyVAZdJeapgYJlwHMpJBwSQNea5/n9W96IkwBf2TQQkGttY957PsK8d74TLQSzr3oT7ae8isevvBDTnyVIKmSFvSBNaKoJN8O0C1ahUBTwaJ85FzVvDvmNT2M7bXhK4zS0sOeXd7HvwfvJ9vaic3m8pjTn3/oLrEmTUMDuJ3/Hsx++AdWYxjQmSbc2I3ftIUgkcIJwDzmkNYsvvZyEk0R7PtJ2GL/yNRx87nlQ4Z4wGYSmWK3UqaU+IAVOvmwI5ge62PgPf8vIYB+p1gmcctPXOf6010KykVM/8488unMzmUeeRKRTIRmvgDd+LAuuejtu1GizXvd69t/8XVTWRygJIjws+/w3/gnz5QCvbxAzMkz7ohM5+9YfIaRNCth049fZddMt2C2tqNYWhNF4wRAPv2UVI4f7UVkXnStw2o3fZsqpZ4YuhNwIv7/+LQzt3YWdTtPUPpZgaASZbsSXPibw0dJCCjj829/y3N98DCvViG87iMYGGttayfbsg4SFMpDIe6WON7hpDWtu+BgyYaPamll+441MPuUsVFsbZ375c9y3/wXE2l0UUgpL+0jXQ0VqnXTeRZxlN/Dch64nn8lhJxoIhF/K7xsIMFJgez5W5HxPBJB1c7ScfCpLP/c5lFDs/P53Wf/J/0ODnSBv53n8V/dy6vd/Su+zT5IeHkY0t8TcDf99N/mfxBEoUKbStxOm8XYSCRwngZeQOIOHefEf/p71//ovJJH4aNqmTGH8tddjAoM0XmxQB1Jg5V2S0xcw5lWnYgAnUCSTjUy59q1YfpKC0lhGY8sAd98eMutfgO4exMAQajiD8sseGxMEiKF+7MOHsHfvJr9mHTqbRUiJNOCqAqKhgbZZC8lFfisNzL/8cszMqQjXBwGuOjIiJ2oALUJI7GSKpoYkDPSx7sc/DUEbDBJJy7yleMUoFQQFN8fUZSeRmBTeVxBow5gps5l0+RUEOTfWmN4LGwk2b8HqO4QY7kfncpRjWgS4BYKhIfRAP6azE3/HDtIDgxTWrMPZux/7cDdysI/wJHD4naUF1kgG0T+I6Oolu+5FvD0HcKQKfU+mIjGDH6BHRggyGazDfcjduxhZ/TxiYBAhRRVQKJWNk06RaHAo9B9iy913hwPSaOxkM2PmLkaXTo+UTUgD+MYw9ZyzOPlr30SNnwj5DLYOraLRubsrgwNMYJh29ZUkLEUBQ+/zL9CkBKbFIZVqIVHweOHzn6Tn/gewE01HHQp+xVwGxaPzqcBghE0+nSCVCthx8y0MbN6CQuIFmoXXvhdryXx03oyKShDk3TyT3nItLcdNxM1lo30EzLr4SlLLlqHzLhhDQRoCWyKSDraysKTCQkbIXYXZZ0u0rcCxsBIOQspwbwCIbI4JC05kzElLcYd6QWg0AS1TZ5JevoScl0fpPxIDj3J8Cq2QjoPZ240bBKWOaxoayyewtSawk0x853VYaHw3gzEGjWDate9BdrRDUD5yoxwbkbDQtkJbsirzlRASS1pIqTAJCxyLQIFMOghHoW1F4KhYRzMCpFAksHCUhUhZaEfgKj/y71ZsA6I4USUk2lEI20YlEwRW3bMWGCGwtAozju09FDsCpexkdT+KOq5GkzeaKeeex8nf+QZeexue7yKNqO8FMAaUomHSZAwhsHbcq86kRymMl0WhcZsUZvOLDG/fSpC0jrrr+hX30/nSkPAljQULJRsJssMcvP8/wxAkDGnb4biLL0J75SgCCWjfIzljFtOvuIz+Qz089+/fxhMBxhiSymLspRejCiHsnfAtbG2htEUgBFoYAmlCxLTStg5kCE0bCwhNHyeQBEKSUwmOf9d1WJ7L8x/9FP1dB1GEJxPmnH8JtoCCMigD8mW2ijAKjMIYG6E1CdXAoDKIwOABemggjFYxgmGdYdyrz+S4k07jwBOPsPM/7g5TnAc+TZOm0X7G6QT5fITGCjQKYULZlZalQSMqzHRhTLRCWbE/0lhYgYUVxENIjAhXiWLCWqnD1S/hRzB/xapSMAqtBZgAEwSkXI9kQdRJagQCiSclngwTTTsdY8tTrQnI7tsDKgw3kYDWIRj2/Pd+gB7KkESS91zGLDmVk/7pCxSkQ1a4WFpFq7uusja0AGsktKQKRjPliss45fNfwp04i8LwALZfQFpNJElioqC7oxk2cgyc4+EsZETxyL1m4MVtUXhV2DXGLliEsGXkTYoGSLafaeddQkt7B3sevJ89372FQm8PktAdMH75GQRNDWEaN1HMiWEiP1y5zFSunpEzTZjQJ4cRBFIjCjnGzF/AlNdeyP7fP8Lue+6ia906vCi/1djlp5FubccEfuxw5kt5AsAVEMiAgDwDXo7Wk5bTLGyMCGUe2rEFUbwbQMPMVauwpWTzz2/nwP0PoAHPCJLAmBVn4YnigIq6l4ln9Krl0hAR/FL8XzgQa3cvMSoBW9GYDI8zlY/OaMAVOZoCgxIaZIJ8KslIayOoMKB9NDPCGJKFAk5ukIAkE1eeFw4uIdj96KP0Pv0MMpko8SEDjRLQc8fPWHvzjWgBjrSxA5j82ouZ8uH3Yw97+MILrQkzyhwRAuF7DOzuxAOSLkjbZsFb38a5N34P58KLCfwkbmGQnOOT8FUpN93/4EEXB2AUksLgSJScJlxJrOYGSDmlU78Yg59waFx5NgFQeOh+9MBBul9YjStAG83EBfNpXXkWJlf4o0xwYQSuBTnHx3NzjDnzTBJI9t7/WxL+ENkHH8IHhB/Q0DGOhosuR4zkQye/eHlqtIMAPy/J2GnmvvcDzP3o+0hEfqVNP76RgScew0k4FHSA0z6VpjPOId/bRfaRJxlet5rM7l0opQgMTL3oApKz56N9P0TsjmEUX6ANU84+n1Me/h1n/vK3rLzrN6z49X286vbbYcwkTK2T545ksKWZkakzWP7FLzHjwgvRaHb95je8+IFPIIwbO/sWKIEL2C2Krq9+la3/9lU8FV6Ion3DSX/9ISa+5124Q3lENCnGgxbCBLQ7bruN3O79ZBMS6Ws8A61z5nLxjT/m1J/8lOZXnYkccfHl0Y/uObaDLjJ7ihtfEcWk2NFp6+LsEuTypM55HRNPOpmeTevoefJxlGOz89Y78IMCUUg9x517DoEwR7xs6g/xo1yNN2EKU664koLrktu0iURzmn3330du8zaMJVHAgrf9FWJ8G54JUPqlN4vQwJixrPjuv3Phr37DqZ/8ByxtOLD2WVb/wyfZ9IUvkTQSywiCfIGON19Oa1MbOx+6F7+/h3xfD7t+8hNUZG5ZzW2MXX4qrld4WVdJ/akeHfh4Qxny2WG8fB/2yDBBPgciKGX9qgRCWuYt4rV3/JxL7vg1c69+I13bN3DXG67ihRs+hJ89EPptKzusNChAKwehDBu/8jVe/NLnMSZAy3AVXvypTzPvk5/Ad31ElPioct2XTgJ/+16eeO+1HH7uESxLkhRgoRFGM3H5qZz2/duYfO21eIX8UT+NYB2L1a08+4RZuGRzC3kEVpDDUSnyvf2YbAY3nSIR+Li2w/Jr341jWTx7480MdXeTTjdx8IGH2X//g0y54EIMMPXcS9gz8yby+7YirWacwA8zfBlGgSi1BpzGCRQj+Rxz33ARbbPmse3O/+DgmrWkkmmGDvaw5gffYeUXv4JnCoydPZtpF13Etlt/TDLV/BJWmGJaPsh7BXY99She9yDuvv34u3eSPbAPcnmakglQCbJBgcbjx3PC299BbrCfdTf/COkVsFSCjbf/hPFvfSMdk6aTxDDzTW+k51e345JDmjTHKmjdkYLdv3+Y1R94H3ayASRYQiEcG8toAtuOcu+GulACBjdsQx7XTnpsB1kT0NwyFn3gEE6mH9OUxAoo7RvDVcdGAQlPMGArSEu2f/ObuAXNkr/9NJYBR1gsft+HKWRG2PjVr2L8AG3A0TAiQWqwUzaZLRt4/O1vZ/d55zP/Qx9n7LTZaKExWpNWCZb/zafp27WTgYd/R5OVxrMChJb/bWvimKZrEIThQqmZ00hF7kwBHNq0FhOEoU9O1sV51Rl0nLIEg+DEN7wdccXlSCnxPZf01DlYJswKnWpqYeL559H5ra04aUMgi3GGL+1xCWhq7GDqqiuwgI6FiznnBz/GEQk87eKPawxhfV8R2NBxxlns/OEvXmKIUDmHZcPwAPtuuhn6+5GOg7YltrSx0qko3M0Q5F06LryY5pYJZLMZzvjkp7EIEIFNTgQ0NbdHje/TMn8erdPn0f/iWkzi2AY7S6lQlsJWVrhfxoDroitSLZiSK0VAppfN//pDJv3bN5DSITluIov/9hNsfu/HMdpFHaH1pAFb25i0Yc/NN9FwXAdzrns3xhcIBYs/8QmGMzmCXNkIEBGQ4kmwEkmU0XT/8m72P/EI01//JuZc/15a2seitUEoi7mXvI5nHnwQCEJU9H+SeVkzIbfReI6iY8Up4eZZOphCnp7/ug9pS2wN2cCjbfnJJFWS4V17sMalSE+ejjNlKi1TZiE8F7Rfch90nH02BSeNQYdBy/qlKcogUJkM9vz5NCw4kXx/H8YtkJo+HTX9eKw500knGvEOdRMaIpqxZ5yDNWMGFAovqzE8y0CjjWhqxE400WAacbRThskDTaNOMP7s1+IB/r5dNE6eRGL6DJLTp9A4bRru4b7Q72QUCTtB8wXnE7jmWOfcKYEV5T+ydv6W4uqYdui+6y46/+NnJKO8NTNfexntV18Z7stGAUKVe7RAGlwFvm2RSBl2fvFLdD73ENIKARfbOKz45N+SOuEEcpUZxooIbqCxkahUK2o4x+5v/StPvfUaBvdtJxCggGTH8UhhY2SACuRR2TP/SVY6Mzp/vAkxPmnCeStQQQi/D+dpO20Zxy8Ps/B6QrD99p9T2LARkU6DD8NNKTpOPBnf83j6ox+kb+NqlOMgjcIKJK4JOOPrX2f8+RdhB5rxi5cx9pTT6X/mIRIqFV1lXMRBxREnA6FtJq66lASSTd/7Huu+/Q0SqTRGaAJh4+WyzLj6ck77/FdxDKimZma88Q28+E+fozXQZGxFItAER+j5IbRvkfQcAp3FKD8chBgsHcLngfHQMyfQfuJSgj17ePitb8MdHsQWCiM0+AbR1sZZP72FpmlLcAxMWbWKPT/9GaZ3L4GdwgkgQFN912s4KIr7afMHJsYjTaCmEgotBhxH91OEWwcLXwXYgULL2hhvIC1sJ8Gub9zEcee+hvTYSQgC5r77WroffpSgZxfYNkpL7KCMehf/3w4Mwig8O4krs3S+/xOMufHbjFtyCq42KCdBY0cSk81VyGswysFIg+sXcIwEmcBqchheu5Yd/3UPC6/7YOjiCvIgdeh+MfHT939WK50pziYRjKyNRAaSgjJ40sL2NN7IAMG4NpZ86P9gko1IIfD6u3nxB7cgpEEbRb6QYfypZzB95Uq2//4R+tetpgEbJwhwfB9pXOzsMJt/9CN87SEk2Ik0i659J0raCA2BKEI0oip+rhIgD/J5nJOWMP/yaxge6WPXr35NozEkfI+k59PoujRK2HvvA/Ts3166Vnf+qmtIzZ6D7xeK97m+hJ1ddBFKMb+BkQijCESYMiPIF5j8uotJNzWx4a7b8Q7sJ6kDVOBhBT6W8NF79tF5x10ReqFpHn88M1ddjVcolK5xLtVRo31Gdx4DL9kfVfXb6OhQAHiBhlwez81Abgg3d5hsdhiCwii7okxM2Q6Z3TvY+L0fRiFehnFTZnPylz6Hm0zheHkgQBirCnE2hH5YpaGJFKZnH49e/172PfUESSlCc14YbKucWVDnCjSdeyZzP/V/yRSyCLwQzDMCR1tYIwVsBAHQ/9QTEBSQRuEfJWj4T2pemqJj2+TxCh7WSI58MMRIOoW18hLOuu1Oxp1xJhbQ/+JGHnrPdai9nYiEQ8IP0AnFgndeD8CeX/wU2+RRIoERTmiySIlqSDP03DMcXr0GX0jAMOasMxm/5DR0PkuIdf1hRo0xTHvnG7DsJF3334e3YzMimSyn9hMSaSWweg+TXb85NBM0OK1tTL30dQxoHyc6BvNSzK/RuTiltnGVQroFUhOOZ/5briOfGaT7nrtJJO0wDk1KJIpAWYgGh6Ff3kdh4HB00yhMuOh8/NYObE/jWjo6KfHKPQoQza3YJ55M6qQzSLz6LMa9bhVTrn8PiQmT0b5fdX1XmITNRzbZHLjlB+x+7CEUFn4ALStWctxVbyI/kiFQHhnbII4gkyslKSuNHjjA4x//AH1bNoa5XYyIXNyhMz/QmvFLT2L2NW+jfeX5ZIYG8XMD5DOHyU4Yw5izz0ECB1c/xe5bf0LSThLIo3fW9U8DpAiJlUqVZsyOZadwxs9+jEyEuTQaxo+neXJ4Z8lIdy/7n32MF7/8zwTbd2I1pihIAb5H29z5THr1uYwc6mHkqWcj351G4pfnCyHQuX56n1zNpJNPAQRp6ZBeeSbq9w8jnGISCoFMOKUhKC27PKMbjdXUzNiTVgCw/94HqvIiKgOukEjhc/D3TzLtgkuQkQ9nzNlnkfj2tzCR+6DWoVZRcauNchJV850RAdL4qKzHuHdcSsuEiex86D68zh0xXRoBllb4TsDAwV0MbXyRphUrSABj55xA49Kl5B99nCAlcXSY31GJ8jGkYu7IP9R/VHSXgAJ0MoGWsvbVWkohpSqt8VNf81qmveYsEpRzv3jAvRtWw67tYUhZdIRGAMq2wwO6wkYXennxx99n2pnnYCloBpa8/wM8+NRz6K0vYBIGETnKkapqFAgMBSWxrCTywH6e/PCHOfPfvk3LrNmIRBJTPMwsJePmzMICzv3yt9l02jkcfOphWlrHsPAt72DcksX07djM+s99Hm9oCDudxJjwPKYv/kwGXezuMSmRGZ/Oh+9HJZvwcLGEjdXYiCdAGUl+7wEOPv0su596goHVj6P3dmMrgdXcRKBBBeAbj8SUqWxZu46R39+PP3gYx0miRRCdJC7X7sgE3aufYt/mV5Mf7MdWDi2TprJr7HiacsPkrIAG16Zn03p69uxC2jZDe3aBCo+0BlrT1NzMyJZdHN64je4X1tLsOPgVZowvNUprjJ1g8Jkn2L3+aXTBBq+ATEra5swhs34DJpGMGWjSgINkcO8udqxdiw487OEBAoLYGiyNCCNKbAfZ1sa2tWvY+8u78IWFQlbsRsK4FlsrXGHoeuR32E0tjAwNkGxo4PiTT2XXI09iNATKIutl2bfuObI5l2Q6jdfdE16FZeqbkUIoBju34CbS6FwByzK4ASS0pqAon/6QCtk3zJZHf0eCNOBiIcMJy4Sn2I1x8MjS0J8li0IL6N60kUPdh5GWIrdjO5YwKBOgky0MrltD12MPQvMYCsMj2M2NzFx1Gdu/sBXHaA6tWc3gcC9uJosj7ZgMUkMgwfEkOt1AsGEDT7z/wyz6l8+F2c8KHqgwIOOFG7/L5HzAhFNPYem172Dpte9AE9C3axeP/NNn6LrjDpzhYURjCoLoxsSjtNKJ+847qzO7Y8dMEgoZ/HHZwOIX/oEvfPoNNBYMru0htKr4rQ1aI7SLpTUikcRSqpQhuRhyFAgBliLI5dFKYqswJUMt7nzlYvsOBTuJLowgjCSdaESTwWhwlaYlrxhOJPHdEZAJgpShMR+UdhdCCnJugDI2ju2CNBht19zhKKPJOQlkVpNReRpVCylZwA18jFBR6FG0fxAShY8mhas9AuNh2za2ySJ1oqQ5pRUFFZDSPiPGxtUSyzIoBZaOm2TR4W98Ab4MowvdQh5p2yScFMl8hrwSJH2Baxs8k8Rzc6RkmoT00cZHj+Jz9IoxklRQkEg/i3QaSWsPjE8QHpIpR9f4PoeNIBkIck5hVMoNTcpNknMMbSKcBKQJCEjj6iwaSFgCpfMok0AaSV4YAiXRWuN7LsKySaXSJHMZtFYEAQzYBdpNiI76ddaNQIBtApSrGWm0SJIgkXPJOD5SO6hshpyySMyYhDNhAtgWuv8w2R17CIYyOAkLJa1o33gU9nJCo4zAF2r7UR90RBEmlgZPanxpUBVTREAUbRHiB1ja4EWpASpRKWksAgQFJ0vKTUWHGGuncshbigYXCjJAKxPutTyJZ0mU0QQyoGBpLN9gpEXCE0gjCVQ5dsUQphlIeQotBYE0dTulpwQy0FgmhP8dzxAogTSqFNNY1o0kkBqpgwi8kFi+wKhi1GhxIIemT94Kc5xY2seXDgKBMhpTsZdRhANOQIjeRSkniPyVnlUMEw83IgaNrzR2oNFCIFAoUwSZarWnCHkUmrxtkMYnkAJbSxxf4lYs0b4MUcUwubuOH+kyYc4aT0o8VcxRE6ACHZ5s0DI0x6VEGIEkCAOUg9JBJAxhnhvXVmG4nSY6SiSjXwR1w/osbWGERuMRCB/Xlihjk/AsXAWWKeD5GsvV2FpTcMKTEcYCX9g0ugalNQUl/vu+z4pBZ5Xj+CW8BPTtpfjhtDAULAiExA5EHCkTxXNjAl2ZbCgWJCcwIkBhSPgORvhHPC7vBEE4SCQkgvB3nh12Ai3CREiOr1DGYAKJZ4Wm4uiO5mjwrSDy49Svz9IaicZXEitQBCqcaAIZDt5KkEujsQOBEeUjIr4VBVjHQACD0oKEZ6GlCc8PaokhdPLLCueuKXuXCYTEVHQKT4bGqKUNvgzTPRkBTiDCg6aRWenJ+nGaBoNvmXC1CFQ08MMZ31Xx/C1OdPORJ8HWFr6ozJYt8FSoaxkx7fgSLSVWEObS8RUlC8Yvhv9ZsmLPK8NJIhAIqdEIbAOB0JFvVtTt5J4VIsrSKECFh5O1IJABRoQ+voSxkMkw0N02Ya4c7QscI9HCJ1BHL9jAlPd00Tr13zBYTdXSXjYVa8GsQeUd3SZUr6kJYYsokuDIDm4Z/aby8GLloNFRVqjoKGN4Dq6uq+MlJGAwAoOK6IT3Z2tRHY1fcuKOWlGkKXbt2FwUWhnF0xfRgCv+PaYXUY6w0KNOTxRXmkAUw6dEiT9M+Xd/CP0uJm4yQhO/bCouYXFCVQa00FWDt6xrEfnlyrNHUV+m4vhB2TzVo2QOT4HIUv858v0+JurTgoobOoo6JgRF0BItym4lUeHHMMKvKe9/N/zRlIGUl+OlOdqBYC/zLBpHsrHr0TtCuakVlPnHrPh/RN11XdLiKJUfbb6OluxHU8Y/To8GU0XhlYnJMlh+roCbLYCvkEZWzVZ/svoFJBNJfD/Arzj5XLyXQCkZu7QwnIwEyUSCQnQ5ZMzEtG2CQEdX4FaYgspCCoE76rpbKQS2bYeXGo7iLZlM4ns+vo5f2mgphZASr4qWxLYtCgU3mrnL7xJOIryg0MQ2rSQcJzTXXC/WN6QUWJaN67nxrhPx5Xl+lYyO7aB1UHU3gKUsLMsiny/E7oQwQCKRiGSP6zFhO2F0UIWMxRQTSqkasgsSiWRYx6iMXAnbwa+8/DJ6ZysLqRQFt1AujtrXcRxctyKsLrqyOeEk8HwvvGOh4p1t2+GlM14hNnykkCQch3yhUMagon1wIpHEdb3Y5SV/+kdHR2oVYve9d3e62exMpRSv5GNLh5u/dxMnnXQSJy5eiq+jK6mExY7ObezYuZPzzrsQVxciy15SKOS5+aabeNvb305zS/kWHkcmuPfee5gyeTLzT1iIb/xSHWvXrKar6yAXXXgJhYiWEJKBgQEefPABrnj9lZgKU8YWNjff9O+c8aoVLDhhUYkvR9i8sPEF+vr6WHnWuSVaUij6D/fxyKOPcMXlVxCY8qUcEsntP/kJF1x0ES1trSV+kzLJnXfdgZVMcMmFl1LQ+QhyUfT1HuLpp57gdZe8viSHAJRQfOffv8MFF17I9GkzSnwlZJL/vOeXTJ8xjYXzF+FGuWVs6bB23fM89/QzXH/9e3CNW0aHteH222/nwkteR3NzC9oEJVo///lPGDd+HGeddW5J95ZQHDh4gN27d7PitFeVaEmh6O3p4bbbbuW9730vjuOUQCRbOtz5Hz9j4aLFzJk9P8z5IjQJmeCZZ55kS+c23vKmt1HQhQhVEOTzeX71q1/x+itej1RWyWy2hc1tP/w+Z55zNlOmTguv3QIc6XDfA/cyNDjIqiveELWJQAmLAwf38Z933cm73v3XIEJABQwWiu/ecjMXXXoJE8YfR2B8XuFnuzX5gkuPWVT6nl//F6edfjaTV54TK+9as45swzMcf8mlsfJsoNn6818y4dKr6Ghpjr3L7N5HcukyJq84LVa+PtVEdssWJo6idWhgkJ6d+5h22ZVVfO2661esfPVrmHzG6bHyLWM6cHfurKJl9/ZxeF83ky+9oopW12NPM/6SKxk/pjVWfnjDJlINaSZeckl85TjUzeHeASZf+voqWjvuuJumc85n8sL4PemD2zpxTj2V41ecESvfkG5i966DHH/pZVW0Dj7xHBMvv5r2xoZYefezq2mdM6dK94Xde9j53HNVtGRXN5vv/jVTrnoTiVEdqff5taTPPp9Jy5fF9/RacMg1VXVkPJ9Dazcx9Yo3VDkC9v72AZpfcxFT5s2NI9fdPfQdOMDES+J85XftovOhx5n2+qurZN97z320X3gpUyZNOib93gpMcGwqFgrb+Ag/nE39aIWwhQK/gIpmcj/iTwqJn8tgG58gn0W3NJdmaEsoZOASFDKxbyyhwM1BVIdngpKpFBSyYVp2DKbiWihLKGwRYNx8FS1dyMX4Lc72QSGLiC4k9Ev6FEghUMYnKGTRtBJE9VtCYWkPFc2yoewiTOaTz6ICr4qWJSSW8dBuroovqT1MjXLj5rEq9GiiFQVjkIGLX8gQNKZLd8dZQiH9QpWMSij8fAbj5WvKbqPDtkmXL4UMabnoQjbSfRj0bguF8PLIUfqShO0rtYfvFsAu+0iVUFjGxxSqZcTLV+jej1a6kC+L0BQ3QhGmcjIooVDGC/sQlPrQK9r35bE8PG5k6UCjrEAoKxK6UeRPIFDRUREpZGSSyMowilIQcmW5oFyuKlLRKSGjX4qSY758t1p4Y+doWrIC5S3zReQxKtYhY3IIEd7FJiNEbRRnZbrRuzAmU1XVUeagjoyj9FWcqIpXAwshSvcYFN0y0ghkVSB4Ld1Hmholu4z2dCKaYEItVLaJrNCjKfGIKLsESj1AhDSIaKgKvkRxRyREDdnVKN2LiF9Vuv3UiOiwdEUouIhJ8UoPumN6AMsgixC5EKX9gBAGUVFe6kQyRBxk8RIQIWLwNDW+EUqMKhcV3dfE6JRABWHKDVypH2lK+7/RfBX5FSLuSI3LUj41Xb6arJpWcfCPbhshTOloWvxd7XIpZZmvUfIbYSJ+RulRlAMGYnqUtfUb/r12m1DxbyEodXkkR2xfpUSVHk29PhG7uLIcHypFKFzpzvEq3dfW8SvxHNscKUYjRs3jxc1+reNXpS5T46S2LK1eozCjQMeS0sRyUZfQK1GxwoZ5TGr5sSSiZiMZbZD1dsaaKHaSUbLWhqplxc05NcFxberoRdTwJ5Yd4HH+THmFGV2/qC2jqCP76MFVT5bK+oWp7WErhmkIU7uj1osLqc1vlB1Nm5gl8Mq5CI7gYDHGdAIzj0Xl737Xuxjo62XmrNmYKExKCklvVzd9vT3MW3hCuN+Kpirf83j44YdZsWIF6XS6fCe3lKxfv56O9rFMmHhc6RshJbt37WJkZISFixZhtMaYACEk2VyGTRtfZPlJJ5dCYkxU/2MPPcKs2bM4btLxMVr79+1jeHiE+Qvmo0swuCCbybBlyxaWLV9e5jd698wTT7FoyWJSjQ2le9WFVKxZvRrLtlm0eFFMxszICNu2bWPpsmUxWkJKHnzgARYvXsLYjrGld1Ip1q5Zw9ixHRxfya9S7N+1mx3bd3DmyrMJinULgdGaZ555hkWLF5NOlXOqCKl49pmnaW5uYe68+RWyCwYG+unt6WXmrJmlSU8IweDwMI8/8Tivee1rsJVd8mkLKXn+mWeYNHkSHcdNQBtdukJ6x/YddHd3c9rpp2N0ed/qeS5r165l+fLlpbvQEeG1a08+/gRz582LyS6kZNPGjeRyOZafdFKsfOBwP2ueW83Z566M7oQwJXfJs888ww9uvY3JU6Yci26/3Tq2Q15w5dXXcM45cfRy/dp1rFu3jre8/W2x8lwux9btO3jP+95Pe3t77N0t3/0u8+fNY8WKFbHyhx58kB07dnLt9ddG995GyFpfL9/73vf56MdvqGJr/979XHn1NZx6ehwJfeyxx9i3bz9vfOMb4khgVxc//clP+MhHP1pF63P/8I9c/573MG78uFhMx799/RukGtJcd911FBdvIeDAvn3cdecveN8HP1zdWrt288a3vIWFCxfGyr/zne+wePHiuOwCHnnwQe75z//kIx/7eKV7FGPgHz7z97z3Ax9kTFtbjNaXvvBFZsyYwVXXXBNzLG/fsYP169dz+WVxlHD/gQPs3L2HD37wI6SSydha85UvfYFzzl3JsuWnlK+0Bn5zz69ZvXo1H/n4x2NWSyaT5Wtf+yof/vgNWJUuLCH49Cf+hje/7W3MXzA/Vv+tt/6QQ4e6IxnLIWo7dmynt7eHj9zwCYQgdofdDR/7eMwH/Irv6Y7xSsuY9nY6xo2LlbWPHUtTc3NVeaFQwEkkGDd+PGPGjIm9a2pqoq0GrdbWNpqaeunoiJdLpUg3NFT9HiCRTNakNaa9naHh4aryQGvSjY01aaVSKcaNG1f1rqGxkXRjdf2e69JYh1YikaB97Niqd431ZG9rI5FM1udr/DjaWuODLp1O09zSQse4jlj50PAwLS0t1fz6Po7jMGHCBBwnfttSuiFNew2+WlpbSTWk6eiI19GYy5FKp5kwYUKVuZpKpRhbQ/am5maGM5mq8uHhoaiv1NajMccuXaE8tgudQOvqzVsQBHXLjTHlCIfKrZPWZZNvdHmRlhlFS+s6e01Tl1atxtJa16WltSnVH7vdqJKvCt6CQNeUvcjXy5W9kl9TsQetR8sYc9TaxOhyeWUmbGNMTT0Wafk1ktIeSfay7k0VrWLC4noXd/7FDbpQ+BqXTIl6MaBFxM/UpCPq7c5FLbqmRt01L7yK11GHr3oxhqIiiDn2/SheSr8RlFwYo+nWq7+u7DV1Fx3YEC9P939I9spg4XK6wcq066Nlrxono9qkyrtUE2H5g3cEVui+UpZjmZb3GJuXhkTCqZp7kkkH27JqmERJlBSkUsmqd7ZtVdCqNBUdrFKqBBGjZZVuO403m1Jh3F61WeLgONU3sCaTiQpaoxRsKZIlfsv1WLbCrsVXOoFl23X5SiYTL132RIJyeF8MW0dZqmIPJmL82nZtGWvJnkomkSKMC62mZeM4yQr8M+LXsct8CarapFb90lYkaspuY1nVekwkkiilSj7ayndKCo6hdXns0ct9+/Ywbdr00twjhGCg7zCHe/uYMW9eGZHC4PseTz/9NMuXLyeZaiijlxi2bdtKa2srHR3jyk5VIThwYB/Dw8PMnTuvFHkBgnw+R2dnJ4sWLiI8dlr+5rmnnmLa9JmMHT++XIcwHOrqIpPJMHPm7FIAsxCCXC7D9u3bOeGEE6rm3vXPP8+c+fNIRAPPGIOUkg0bN2Api3nz5lXIIcjlsuzatYv58xeMioQXPPXUE8ydO4+2MWMr+ILNL26ibcwYxo8fjzFlOboOHGDfnt2cdNqpcTPTGNauXcsJCxaE+5uSn0yyYd06GhuamDpzZkz24aEhDh8+zNRp00sdVghBZmSY559fzRlnnIFS5dSwQgg2rnuBCccdR/u4jgpakr1799DXe5ilJy6NysOV3vd9Nm3axAkLF5fRy2jlfH71ambMmEHbmPaK+mF75zZyuRyLFi2KvCmhj294aIhN61/g1NNPq7AcQpfLpvXrufVntzN58uS/PPTSYDjz1a/m1FNPA6NLd4Fv27KZzq2dXHjJJRUdEgqFHDt27ODii18XKb/87u6772LGjBksWrwk1imefvopuroOctlll5cGnRCCw4cP8+t77uHKq66MHQ4RSPbv3sOrzjyThYsXxzr3C+vW0tXVxXnnX1hRLujpOcT999/PqlVXR+XlSIrhw4e5+HUXR/zqUsfzPI9EIsEVV1wZ+SsBIent6ebBBx/kqlWryr8nTE2wc+cOVp57LjNnzo7x9Ys7fs6cuXNZPEr25599lid0wFVXrYrJ7vs+AwMDvO51r6OltS2m+3wmw8TjJnLOa8+L1bF/3162bdvG2WevjA2sQ10H2b17F6+/4gocO1EKHhBC4mZznLhsKQsWLorJ/thjj7Jl81auvOrK8skqYcjlcuTzea688gqUsipMTkFvdw/nrjyXGTNnxVDg3/zmHgYGBrjyqlUl3Qsh2L9vH72Hunj9FVeiLIUxIR1jDN851E3g+8es3x/TQSel4vTTV3DWWWfFyse1d2BbiSpXgjGG733/h5x3/vk0NjbF3m3esoUlS5ZwxhlnVG20t27dyjnnrKxCtzZufJGVK19TxdftP/kpp556Gqecdmqs3HES7Ny5s4qvw4cP09m5o6oOgN/99j7OXflaWtpaY+XPPfscDY2NVd/0dHezd9eumrR++MMfsWLFq5g/f0GsfN26Fzj55FOqZJcIOrd11qR1/33389rzL6AhHQ94fuyhR5g7b16VjHv27CHd0MQ5K0fx29PD7T+/g/PPv7CqjicefYQVK87gxGUnx8qzI1nyuUIVrSAIePyJJ3nta8+rovWrO3/Jq199NrPnzomV79y1gwMHDlTJuHfPbu679ze8pgatO26/oyYo8xcDpBQKhZplXg0/Si6XQ2tNLpeveud5Xk1aruvWoZWviZIVG//l8JXP16fl+z65XK4KFvE9P04repH/A3zl84WaddTjt7JzVaKXgR+U+BpNy3XdmjLWKw/bJHdEvirRS9d1a8qYy+Xwfb/mu1D22u1e/r2J8RUi1NXoZT10+C9m0P3//hhTO0Tqf58j6cz8fy2fBNJ/LsotA9gaw9Fb/mt1+nq+onCvbV5Wwx+JlhFBDOoWFfvZKuy79j/+YD0vlVcxStd1c1y9TNmPWKMRVdC+wVSd/H+JDVmHVVFHb3XiLaU4li6DtAVsBrJ/LoOumHat3gWHIorFe6mD6+WsMpWhQjUDeKV82auWqDiZEC+Xdfa5Euqkghc10rH/ofKaQcqCmjfplOsXL3lw1as7lFHEjKnyyakjfHOEclEHFxA1b8IVSKkqUqcdefC+gs+e/zcA2ghOVoD+wwYAAAAASUVORK5CYII="

st.markdown("""
<style>
.header-bar {
    display:flex; align-items:center; justify-content:space-between;
    background:linear-gradient(90deg,#6b0000,#cc0000,#6b0000);
    padding:12px 20px; border-radius:10px; margin-bottom:16px;
}
.header-title { color:white; font-size:22px; font-weight:800; letter-spacing:2px; }
.header-sub   { color:#ffcccc; font-size:11px; margin-top:3px; }
.dp-logo      { height:42px; border-radius:4px; }
</style>
""", unsafe_allow_html=True)

st.markdown(f'''<div class="header-bar">
  <div>
    <div class="header-title">\U0001f50c SolderSense AI</div>
    <div class="header-sub">PCB Defect Detection &nbsp;|&nbsp; Data Patterns</div>
  </div>
  <img src="data:image/png;base64,{DP_LOGO_B64}" class="dp-logo" alt="Data Patterns"/>
</div>''', unsafe_allow_html=True)

PROJECT  = "pcb-dataset-defect-ddykw"
VERSION  = 2
DB_PATH  = "inspections.db"

CLASS_COLORS = {
    "missing_hole":(255,50,50),"mouse_bite":(255,165,0),
    "open_circuit":(50,50,255),"short":(50,200,50),
    "spur":(180,50,255),"spurious_copper":(0,220,220),
}

def init_db():
    c = sqlite3.connect(DB_PATH)
    c.execute("""CREATE TABLE IF NOT EXISTS inspections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT, filename TEXT, verdict TEXT,
        defect_count INTEGER, defect_classes TEXT, confidence REAL)""")
    c.commit(); c.close()

def save_inspection(filename, verdict, n, classes, conf):
    c = sqlite3.connect(DB_PATH)
    c.execute("INSERT INTO inspections VALUES (NULL,?,?,?,?,?,?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), filename, verdict, n,
         ",".join(classes) if classes else "none", conf))
    c.commit(); c.close()

def call_roboflow(img_bytes, api_key, conf=35):
    resp = requests.post(
        f"https://detect.roboflow.com/{PROJECT}/{VERSION}",
        params={"api_key":api_key,"confidence":conf},
        files={"file":img_bytes}, timeout=30)
    return resp.json() if resp.status_code == 200 else None

def draw_boxes(img_pil, data, orig_w, orig_h):
    img  = img_pil.copy().convert("RGB")
    draw = ImageDraw.Draw(img)
    aw   = data.get("image",{}).get("width",  orig_w)
    ah   = data.get("image",{}).get("height", orig_h)
    sx, sy = orig_w/aw, orig_h/ah
    for p in data.get("predictions",[]):
        cls = p["class"]; conf = p["confidence"]
        x  = (p["x"]-p["width"] /2)*sx; y  = (p["y"]-p["height"]/2)*sy
        x2 = (p["x"]+p["width"] /2)*sx; y2 = (p["y"]+p["height"]/2)*sy
        col = CLASS_COLORS.get(cls,(255,255,0))
        draw.rectangle([x,y,x2,y2], outline=col, width=3)
        lbl = f"{cls} {conf:.2f}"
        draw.rectangle([x,y-22,x+len(lbl)*8,y], fill=col)
        draw.text((x+3,y-19), lbl, fill="white")
    return img

def generate_pdf(df, logo_b64):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
          topMargin=18*mm, bottomMargin=18*mm,
          leftMargin=18*mm, rightMargin=18*mm)
    story = []
    rl_logo = RLImage(io.BytesIO(base64.b64decode(logo_b64)), width=48*mm, height=14*mm)
    t_s = ParagraphStyle("t",fontSize=16,fontName="Helvetica-Bold",
                         textColor=colors.HexColor("#cc0000"),alignment=TA_LEFT)
    s_s = ParagraphStyle("s",fontSize=8,fontName="Helvetica",
                         textColor=colors.HexColor("#666666"),alignment=TA_LEFT)
    hdr = Table([[
        [Paragraph("SolderSense AI",t_s),
         Paragraph("PCB Defect Detection System  |  Data Patterns",s_s)],
        rl_logo]], colWidths=[118*mm,52*mm])
    hdr.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("ALIGN",(1,0),(1,0),"RIGHT"),
        ("LINEBELOW",(0,0),(-1,0),1,colors.HexColor("#cc0000")),
        ("BOTTOMPADDING",(0,0),(-1,0),6)]))
    story.append(hdr); story.append(Spacer(1,5*mm))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ms  = ParagraphStyle("ms",fontSize=9,textColor=colors.HexColor("#333333"))
    pn  = len(df[df["verdict"]=="PASS"])
    fn  = len(df[df["verdict"]=="FAIL"])
    rn  = len(df[df["verdict"]=="REVIEW"])
    rt  = f"{100*pn/len(df):.1f}%" if len(df) else "N/A"
    story += [
        Paragraph(f"<b>Report Generated:</b> {now}", ms),
        Paragraph(f"<b>Total:</b> {len(df)}  <b>Pass:</b> {pn}  <b>Fail:</b> {fn}  <b>Review:</b> {rn}  <b>Pass Rate:</b> {rt}", ms),
        Spacer(1,4*mm),
        HRFlowable(width="100%",thickness=0.5,color=colors.HexColor("#cccccc")),
        Spacer(1,4*mm),
        Paragraph("Inspection Log", ParagraphStyle("h2",fontSize=12,
            fontName="Helvetica-Bold",textColor=colors.HexColor("#8b0000"))),
        Spacer(1,3*mm),
    ]
    rows = [["#","Timestamp","Filename","Verdict","Defects","Classes","Conf"]]
    for _,r in df.iterrows():
        rows.append([str(r.get("id","")),str(r.get("timestamp",""))[:16],
            str(r.get("filename",""))[:25],str(r.get("verdict","")),
            str(r.get("defect_count",0)),str(r.get("defect_classes",""))[:28],
            f"{float(r.get('confidence',0)):.2f}"])
    tbl = Table(rows,colWidths=[10,35,44,20,15,42,14],repeatRows=1)
    vc  = {"PASS":colors.HexColor("#d4edda"),"FAIL":colors.HexColor("#f8d7da"),
            "REVIEW":colors.HexColor("#fff3cd")}
    ts  = [("BACKGROUND",(0,0),(-1,0),colors.HexColor("#8b0000")),
           ("TEXTCOLOR",(0,0),(-1,0),colors.white),
           ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
           ("FONTSIZE",(0,0),(-1,-1),7),("ALIGN",(0,0),(-1,-1),"CENTER"),
           ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
           ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f9f9f9")]),
           ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#cccccc")),
           ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)]
    for i,row in enumerate(rows[1:],1):
        if row[3] in vc: ts.append(("BACKGROUND",(3,i),(3,i),vc[row[3]]))
    tbl.setStyle(TableStyle(ts)); story.append(tbl)
    story += [Spacer(1,8*mm),
        HRFlowable(width="100%",thickness=0.5,color=colors.HexColor("#cccccc")),
        Spacer(1,3*mm),
        Paragraph(f"Confidential — SolderSense AI  |  Data Patterns  |  {now}",
            ParagraphStyle("ft",fontSize=7,alignment=TA_CENTER,
                           textColor=colors.HexColor("#999999")))]
    doc.build(story); buf.seek(0); return buf.read()

init_db()

tab1, tab2, tab3 = st.tabs(["\U0001f50d Live Inspection","\U0001f4ca History","\U0001f4e5 Export Report"])

with tab1:
    col_l, col_r = st.columns([1,2])
    with col_l:
        st.markdown("#### Settings")
        api_key  = st.text_input("Roboflow API Key", type="password")
        conf_val = st.slider("Confidence Threshold", 10, 80, 35)
        uploaded = st.file_uploader("Upload PCB Image", type=["jpg","jpeg","png"])
        st.caption("Detects: missing\_hole · mouse\_bite · open\_circuit · short · spur · spurious\_copper")
    with col_r:
        if uploaded and api_key:
            img_bytes = uploaded.read()
            img_pil   = Image.open(io.BytesIO(img_bytes))
            orig_w, orig_h = img_pil.size
            with st.spinner("Running SolderSense AI inference…"):
                t0   = time.time()
                data = call_roboflow(img_bytes, api_key, conf_val)
                elapsed = time.time() - t0
            if data is None:
                st.error("API call failed. Check your API key.")
            else:
                preds = data.get("predictions",[])
                dp    = [p for p in preds if p["class"] != "good"]
                if not dp:
                    verdict = "PASS"; st.success("## \u2705 PASS")
                elif max(p["confidence"] for p in dp) >= 0.70:
                    verdict = "FAIL"; st.error("## \u274c FAIL")
                else:
                    verdict = "REVIEW"; st.warning("## \u26a0\ufe0f REVIEW")
                st.caption(f"Inference: {elapsed:.2f}s | Detections: {len(dp)}")
                st.image(draw_boxes(img_pil,data,orig_w,orig_h),
                         caption="Annotated Result", use_column_width=True)
                if dp:
                    st.dataframe(pd.DataFrame([{
                        "Class":p["class"],"Confidence":f'{p["confidence"]:.2f}',
                        "X":int(p["x"]),"Y":int(p["y"])
                    } for p in dp]), use_container_width=True)
                classes  = list(set(p["class"] for p in dp))
                avg_conf = round(sum(p["confidence"] for p in dp)/len(dp),3) if dp else 0.0
                save_inspection(uploaded.name, verdict, len(dp), classes, avg_conf)
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
        c1,c2,c3 = st.columns(3)
        c1.metric("Total Inspections", len(df))
        c2.metric("Defects Found", len(df[df["verdict"]=="FAIL"]))
        c3.metric("Pass Rate", f'{100*len(df[df["verdict"]=="PASS"])/len(df):.1f}%')
        st.bar_chart(df["verdict"].value_counts())
        st.dataframe(df, use_container_width=True)

with tab3:
    conn = sqlite3.connect(DB_PATH)
    df   = pd.read_sql("SELECT * FROM inspections ORDER BY id DESC", conn)
    conn.close()
    st.markdown("#### Export Defect Report")
    if df.empty:
        st.info("No data to export yet.")
    else:
        c1,c2 = st.columns(2)
        with c1:
            st.download_button("\U0001f4e5 Download CSV",
                df.to_csv(index=False),"soldersense_report.csv","text/csv",
                use_container_width=True)
        with c2:
            pdf_bytes = generate_pdf(df, DP_LOGO_B64)
            st.download_button("\U0001f4c4 Download PDF Report",
                pdf_bytes,"soldersense_defect_report.pdf","application/pdf",
                use_container_width=True)
        st.caption("PDF includes Data Patterns logo, summary and full inspection log.")

st.markdown("<br><center style=\'color:#444;font-size:11px\'>SolderSense AI &nbsp;|&nbsp; Data Patterns &nbsp;|&nbsp; Confidential</center>",unsafe_allow_html=True)
