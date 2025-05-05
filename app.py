import streamlit as st
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from io import BytesIO
import base64
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms.ollama import Ollama

st.set_page_config(page_title="FashionFit Palette", layout="wide")
st.title("🎨 FashionFit Palette - Outfit Color Analyzer & Suggestor")

# Upload section
uploaded_image = st.file_uploader("📸 Upload Your Fashion Image", type=["jpg", "jpeg", "png"])

# Helper to extract dominant colors
def get_dominant_colors(img, n_colors=5):
    img = img.resize((150, 150))
    img_np = np.array(img).reshape(-1, 3)
    kmeans = KMeans(n_clusters=n_colors, random_state=42).fit(img_np)
    colors = kmeans.cluster_centers_.astype(int)
    return colors

# Helper to show color palette
def display_palette(colors):
    fig, ax = plt.subplots(1, figsize=(6, 2))
    for i, color in enumerate(colors):
        ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=color/255))
    plt.xlim(0, len(colors))
    plt.axis("off")
    st.pyplot(fig)

# Helper for season suggestion
def suggest_season(colors):
    avg_color = np.mean(colors, axis=0)
    if avg_color[0] > 200:
        return "Summer"
    elif avg_color[1] > 200:
        return "Spring"
    elif avg_color[2] > 200:
        return "Winter"
    else:
        return "Fall"

# Generate blog/caption with LLM
def generate_caption(color_list):
    prompt = PromptTemplate(
        input_variables=["colors"],
        template="Write a trendy 50-word fashion tip or Instagram caption for an outfit with these main colors: {colors}."
    )
    llm = Ollama(model="tinyllama")
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run({"colors": ', '.join(color_list)})

if uploaded_image:
    img = Image.open(uploaded_image).convert("RGB")
    st.image(img, caption="Uploaded Image", use_container_width=True)

    with st.spinner("🔍 Analyzing Colors..."):
        colors = get_dominant_colors(img)
        hex_colors = ["#%02x%02x%02x" % tuple(c) for c in colors]

        st.subheader("🎯 Detected Color Palette")
        display_palette(colors)
        st.write("Hex Codes:", ", ".join(hex_colors))

        season = suggest_season(colors)
        st.info(f"👗 Best Worn In: **{season}**")

        st.subheader("✍️ AI-Generated Fashion Tip")
        caption = generate_caption(hex_colors)
        st.success(caption)

        # Downloadable palette as image
        st.subheader("📥 Download Palette")
        fig, ax = plt.subplots(figsize=(5, 1))
        for i, color in enumerate(colors):
            ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=color / 255))
        plt.xlim(0, len(colors))
        plt.axis('off')
        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode()
        href = f'<a href="data:image/png;base64,{b64}" download="palette.png">⬇️ Download Color Palette</a>'
        st.markdown(href, unsafe_allow_html=True)
