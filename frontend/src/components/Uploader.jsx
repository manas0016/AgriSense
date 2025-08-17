import { useState } from "react";
import axios from "axios";

function UploadCSV() {
  const [file, setFile] = useState(null);

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("http://localhost:8000/ingest/file", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      console.log("Uploaded:", res.data);
    } catch (err) {
      console.error("Upload error:", err);
    }
  };

  return (
    <div>
      <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload}>Upload CSV</button>
    </div>
  );
}

export default UploadCSV;
