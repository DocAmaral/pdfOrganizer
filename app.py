import streamlit as st
from pypdf import PdfReader, PdfWriter
import io

st.set_page_config(page_title="PDF Page Organizer", layout="wide")

st.title("📄 PDF Page Organizer")
st.write("Upload one or more PDFs and create custom ordered output files.")

# Upload PDFs
uploaded_files = st.file_uploader(
    "Upload PDF files",
    type="pdf",
    accept_multiple_files=True
)

if uploaded_files:

    readers = []
    file_info = []

    # Read PDFs
    for i, file in enumerate(uploaded_files):
        reader = PdfReader(file)
        readers.append(reader)
        file_info.append({
            "name": file.name,
            "pages": len(reader.pages)
        })

    st.subheader("📚 Uploaded Files")

    for idx, info in enumerate(file_info):
        st.write(f"**File {idx+1}: {info['name']}** — {info['pages']} pages")

    st.divider()

    st.subheader("🛠 Create Output PDFs")

    num_outputs = st.number_input(
        "How many output PDFs do you want?",
        min_value=1,
        value=1,
        step=1
    )

    outputs = []

    for i in range(int(num_outputs)):
        st.markdown(f"### Output File {i+1}")

        name = st.text_input(
            f"Output file {i+1} name",
            value=f"output_{i+1}.pdf",
            key=f"name_{i}"
        )

        page_input = st.text_area(
            f"Pages for output {i+1}",
            placeholder="Example: 1:1, 1:3, 2:5",
            key=f"pages_{i}"
        )

        outputs.append((name, page_input))

    if st.button("Generate PDFs"):

        for name, page_input in outputs:

            writer = PdfWriter()

            if not page_input.strip():
                st.warning(f"No pages specified for {name}")
                continue

            entries = [x.strip() for x in page_input.split(",")]

            try:
                for entry in entries:
                    file_idx, page_num = entry.split(":")
                    file_idx = int(file_idx) - 1
                    page_num = int(page_num) - 1

                    reader = readers[file_idx]

                    if page_num < 0 or page_num >= len(reader.pages):
                        st.error(f"Invalid page number in {entry}")
                        continue

                    writer.add_page(reader.pages[page_num])

                buffer = io.BytesIO()
                writer.write(buffer)
                buffer.seek(0)

                st.download_button(
                    label=f"Download {name}",
                    data=buffer,
                    file_name=name,
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(f"Error processing {name}: {e}")