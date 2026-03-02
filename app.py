import streamlit as st
from pypdf import PdfReader, PdfWriter
from pdf2image import convert_from_bytes
from streamlit_sortables import sort_items
from PIL import Image
import io

st.set_page_config(layout="wide")
st.title("📄 Visual PDF Page Organizer")

uploaded_files = st.file_uploader(
    "Upload PDF files",
    type="pdf",
    accept_multiple_files=True
)

if uploaded_files:

    if "page_pool" not in st.session_state:
        st.session_state.page_pool = []
        st.session_state.page_map = {}

        for file_index, file in enumerate(uploaded_files):
            reader = PdfReader(file)
            pages = convert_from_bytes(file.read(), dpi=60)

            for page_index, img in enumerate(pages):
                label = f"F{file_index+1}-P{page_index+1}"
                thumb = img.resize((150, 200))

                buffer = io.BytesIO()
                thumb.save(buffer, format="PNG")

                st.session_state.page_pool.append(label)
                st.session_state.page_map[label] = {
                    "file_index": file_index,
                    "page_index": page_index,
                    "image": buffer.getvalue()
                }

    st.subheader("🗂 Drag Pages to Reorder (Pool)")
    st.write("Drag to reorder. You will assign pages to outputs below.")

    st.session_state.page_pool = sort_items(
        st.session_state.page_pool,
        direction="horizontal"
    )

    # Display thumbnails
    cols = st.columns(6)
    for i, label in enumerate(st.session_state.page_pool):
        with cols[i % 6]:
            st.image(st.session_state.page_map[label]["image"])
            st.caption(label)

    st.divider()

    st.subheader("📦 Create Output Files")

    num_outputs = st.number_input(
        "Number of output PDFs",
        min_value=1,
        value=1,
        step=1
    )

    output_structures = []

    for i in range(int(num_outputs)):
        st.markdown(f"### Output File {i+1}")
        name = st.text_input(
            f"Filename for Output {i+1}",
            value=f"output_{i+1}.pdf",
            key=f"name_{i}"
        )

        selected_pages = st.multiselect(
            "Select pages in desired order",
            options=st.session_state.page_pool,
            key=f"select_{i}"
        )

        output_structures.append((name, selected_pages))

    if st.button("Generate PDFs"):

        for name, selected_pages in output_structures:

            writer = PdfWriter()

            for label in selected_pages:
                data = st.session_state.page_map[label]
                reader = PdfReader(uploaded_files[data["file_index"]])
                writer.add_page(reader.pages[data["page_index"]])

            buffer = io.BytesIO()
            writer.write(buffer)
            buffer.seek(0)

            st.download_button(
                label=f"Download {name}",
                data=buffer,
                file_name=name,
                mime="application/pdf"
            )