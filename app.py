import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
import pypdf
import io
import os
import zipfile

# Konfigurasi explicit path Tesseract untuk Linux (Streamlit Cloud)
if os.path.exists('/usr/bin/tesseract'):
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# Konfigurasi Halaman
st.set_page_config(page_title="Toolku", page_icon="🛠️", layout="wide")

st.title("🛠️ Toolku: All-in-One File Utility & OCR")
st.write("Aplikasi web serbaguna untuk konversi dokumen, pengolahan gambar, manipulasi PDF, dan ekstraksi teks.")

# Sidebar Menu Navigasi
menu = st.sidebar.selectbox(
    "Pilih Menu:",
    [
        "Konversi Dokumen & Data",
        "Pengolah Gambar",
        "Manipulasi PDF",
        "Pengganti Nama Massal",
        "OCR Cerdas"
    ]
)

# 1. Konversi Dokumen & Data
if menu == "Konversi Dokumen & Data":
    st.header("📄 Konversi Dokumen & Data")
    sub_menu = st.selectbox("Pilih Format:", ["Excel ke CSV", "CSV ke Excel"])
    
    if sub_menu == "Excel ke CSV":
        uploaded_file = st.file_uploader("Unggah file Excel (.xlsx / .xls)", type=["xlsx", "xls"])
        if uploaded_file is not None:
            df = pd.read_excel(uploaded_file)
            st.dataframe(df)
            
            # Menggunakan key agar nilainya langsung tersinkronisasi secara real-time
            custom_name = st.text_input("Nama file hasil unduhan:", value="converted_data", key="excel_to_csv_name")
            csv = df.to_csv(index=False).encode('utf-8')
            
            final_filename = f"{custom_name.strip() or 'converted_data'}.csv"
            st.download_button(
                "Unduh Hasil CSV", 
                data=csv, 
                file_name=final_filename, 
                mime="text/csv"
            )
            
    elif sub_menu == "CSV ke Excel":
        uploaded_file = st.file_uploader("Unggah file CSV (.csv)", type=["csv"])
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df)
            
            custom_name = st.text_input("Nama file hasil unduhan:", value="converted_data", key="csv_to_excel_name")
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
            processed_data = output.getvalue()
            
            final_filename = f"{custom_name.strip() or 'converted_data'}.xlsx"
            st.download_button(
                "Unduh Hasil Excel", 
                data=processed_data, 
                file_name=final_filename, 
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# 2. Pengolah Gambar
elif menu == "Pengolah Gambar":
    st.header("🖼️ Pengolah & Kompresor Gambar")
    uploaded_files = st.file_uploader("Unggah gambar (Bisa banyak sekaligus)", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)
    
    if uploaded_files:
        target_format = st.selectbox("Pilih Format Output:", ["PNG", "JPEG", "WEBP"])
        quality = st.slider("Kualitas Kompresi (Untuk JPEG/WEBP):", 10, 100, 85)
        
        # Label dinamis tergantung jumlah file
        is_single = len(uploaded_files) == 1
        label_input = "Nama file hasil unduhan:" if is_single else "Nama file ZIP hasil unduhan:"
        default_name = os.path.splitext(uploaded_files[0].name)[0] if is_single else "processed_images"
        
        custom_name = st.text_input(label_input, value=default_name, key="image_custom_name")
        
        if st.button("Proses Gambar"):
            if is_single:
                # Proses 1 file gambar tunggal
                file = uploaded_files[0]
                img = Image.open(file)
                if target_format == "JPEG" and img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                output_io = io.BytesIO()
                img.save(output_io, format=target_format, quality=quality)
                
                final_name = f"{custom_name.strip() or default_name}.{target_format.lower()}"
                
                # Tentukan mime type yang sesuai
                mime_types = {"PNG": "image/png", "JPEG": "image/jpeg", "WEBP": "image/webp"}
                
                st.download_button(
                    label=f"Unduh Gambar ({target_format})",
                    data=output_io.getvalue(),
                    file_name=final_name,
                    mime=mime_types.get(target_format, "image/jpeg")
                )
            else:
                # Proses banyak file menjadi ZIP
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for file in uploaded_files:
                        img = Image.open(file)
                        if target_format == "JPEG" and img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                        
                        output_io = io.BytesIO()
                        img.save(output_io, format=target_format, quality=quality)
                        
                        file_name = os.path.splitext(file.name)[0] + f".{target_format.lower()}"
                        zf.writestr(file_name, output_io.getvalue())
                
                final_zip_name = f"{custom_name.strip() or 'processed_images'}.zip"
                st.download_button(
                    label="Unduh Semua Gambar (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name=final_zip_name,
                    mime="application/zip"
                )

# 3. Manipulasi PDF
elif menu == "Manipulasi PDF":
    st.header("📑 Manipulasi PDF (Merge & Split)")
    pdf_menu = st.selectbox("Pilih Aksi:", ["Gabung PDF (Merge)", "Pisah PDF (Split)"])
    
    if pdf_menu == "Gabung PDF (Merge)":
        pdf_files = st.file_uploader("Unggah file PDF untuk digabungkan", type=["pdf"], accept_multiple_files=True)
        if pdf_files:
            custom_name = st.text_input("Nama file PDF gabungan:", value="merged_document", key="merge_pdf_name")
            if st.button("Gabungkan PDF"):
                # Menggunakan PdfWriter untuk menggabungkan file di pypdf versi baru
                merger = pypdf.PdfWriter()
                for pdf in pdf_files:
                    merger.append(pdf)
                output_io = io.BytesIO()
                merger.write(output_io)
                merger.close()
                st.download_button(
                    "Unduh PDF Gabungan", 
                    data=output_io.getvalue(), 
                    file_name=f"{custom_name.strip() or 'merged_document'}.pdf", 
                    mime="application/pdf"
                )
            
    elif pdf_menu == "Pisah PDF (Split)":
        pdf_file = st.file_uploader("Unggah satu file PDF untuk dipisah", type=["pdf"])
        if pdf_file:
            reader = pypdf.PdfReader(pdf_file)
            total_pages = len(reader.pages)
            st.info(f"Total halaman dalam PDF: **{total_pages}**")
            
            split_mode = st.radio("Pilih Mode Split:", ["Halaman Tunggal", "Rentang Halaman (Range)"])
            
            if split_mode == "Halaman Tunggal":
                page_num = st.number_input("Pilih nomor halaman:", min_value=1, max_value=total_pages, value=1, key="single_page_num")
                
                with st.expander(f"👁️ Preview Konten Halaman {page_num}", expanded=True):
                    try:
                        preview_text = reader.pages[page_num - 1].extract_text()
                        if preview_text.strip():
                            st.text_area("Isi Teks Halaman Ini:", value=preview_text, height=150, disabled=True)
                        else:
                            st.warning("Halaman ini tidak mengandung teks yang bisa diekstrak (kemungkinan berupa gambar/scan murni).")
                    except Exception as e:
                        st.error(f"Gagal memuat preview: {e}")
                
                custom_name = st.text_input("Nama file hasil PDF:", value=f"page_{page_num}", key="single_split_name")
                
                if st.button("Proses & Unduh Halaman"):
                    writer = pypdf.PdfWriter()
                    writer.add_page(reader.pages[page_num - 1])
                    output_io = io.BytesIO()
                    writer.write(output_io)
                    writer.close()
                    
                    st.download_button(
                        f"Unduh Halaman {page_num}", 
                        data=output_io.getvalue(), 
                        file_name=f"{custom_name.strip() or f'page_{page_num}'}.pdf", 
                        mime="application/pdf"
                    )
                    
            elif split_mode == "Rentang Halaman (Range)":
                range_input = st.text_input("Masukkan rentang halaman (Contoh: 1-5 atau 1,3,5-7):", value="1-3", key="range_input_text")
                custom_name = st.text_input("Nama file PDF hasil rentang:", value="split_document", key="range_split_name")
                
                if st.button("Proses & Unduh Rentang PDF"):
                    writer = pypdf.PdfWriter()
                    pages_to_extract = set()
                    
                    try:
                        parts = range_input.split(",")
                        for part in parts:
                            if "-" in part:
                                start, end = map(int, part.split("-"))
                                for p in range(start, end + 1):
                                    if 1 <= p <= total_pages:
                                        pages_to_extract.add(p - 1)
                            else:
                                p = int(part.strip())
                                if 1 <= p <= total_pages:
                                    pages_to_extract.add(p - 1)
                        
                        sorted_pages = sorted(list(pages_to_extract))
                        
                        if sorted_pages:
                            for idx in sorted_pages:
                                writer.add_page(reader.pages[idx])
                            
                            output_io = io.BytesIO()
                            writer.write(output_io)
                            writer.close()
                            
                            st.download_button(
                                "Unduh PDF Berdasarkan Rentang",
                                data=output_io.getvalue(),
                                file_name=f"{custom_name.strip() or 'split_document'}.pdf",
                                mime="application/pdf"
                            )
                        else:
                            st.warning("Rentang halaman tidak valid atau di luar batas total halaman.")
                    except Exception as e:
                        st.error(f"Format rentang halaman salah. Gunakan format seperti '1-3' atau '1,2,4'. Error: {e}")
                        
# 4. Pengganti Nama Massal
elif menu == "Pengganti Nama Massal":
    st.header("🏷️ Pengganti Nama Massal (Batch Renamer)")
    uploaded_files = st.file_uploader("Unggah file yang ingin diubah namanya", accept_multiple_files=True)
    
    prefix = st.text_input("Prefix (Awalan nama baru):", value="file_")
    custom_name = st.text_input("Nama file ZIP hasil unduhan:", value="renamed_files")
    
    if uploaded_files and st.button("Proses Ganti Nama"):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for idx, file in enumerate(uploaded_files, start=1):
                ext = os.path.splitext(file.name)[1]
                new_name = f"{prefix}{idx}{ext}"
                zf.writestr(new_name, file.getvalue())
                
        st.download_button(
            label="Unduh File Ter-rename (ZIP)",
            data=zip_buffer.getvalue(),
            file_name=f"{custom_name.strip() or 'renamed_files'}.zip",
            mime="application/zip"
        )

# 5. OCR Cerdas
elif menu == "OCR Cerdas":
    st.header("🔍 OCR Cerdas (Ekstrak Teks dari Gambar)")
    uploaded_image = st.file_uploader("Unggah gambar berisi teks", type=["png", "jpg", "jpeg"])
    
    if uploaded_image:
        img = Image.open(uploaded_image)
        st.image(img, caption="Gambar yang Diunggah", use_container_width=True)
        
        custom_name = st.text_input("Nama file teks hasil OCR:", value="extracted_text")
        
        if st.button("Ekstrak Teks"):
            with st.spinner("Sedang memproses OCR..."):
                try:
                    extracted_text = pytesseract.image_to_string(img)
                except Exception as e:
                    extracted_text = ""
                    st.error(f"Gagal menjalankan OCR. Pastikan paket system Tesseract terinstal. Error: {e}")
            
            if extracted_text.strip():
                st.subheader("Hasil Teks:")
                st.code(extracted_text, language="text")
                
                st.download_button(
                    label="📥 Unduh Teks (.txt)", 
                    data=extracted_text, 
                    file_name=f"{custom_name.strip() or 'extracted_text'}.txt", 
                    mime="text/plain"
                )
            else:
                st.warning("Tidak ada teks yang berhasil dideteksi dari gambar tersebut. Coba gunakan gambar dengan resolusi yang lebih jelas.")
