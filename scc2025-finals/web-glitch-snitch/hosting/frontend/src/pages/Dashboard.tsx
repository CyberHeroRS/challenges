import { useState } from "react";
import config from "../config";
import useFetch from "../hooks/useFetch";

const fileDownloadURL = (filename: string) =>
  `${config.BACKEND_URL}/uploads/${filename}`;

export default function Dashboard() {
  
  const {
    data: data,
    loading,
    refetch,
  } = useFetch<{
    files: string[];
  }>("/myuploads");
  const [file, setFile] = useState<File | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFile(event.target.files[0]);
    }
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!file) {
      return;
    }

    // Check file size - must be less than 5MB
    if (file.size > 5 * 1024 * 1024) {
      alert("File size must be less than 5MB");
      return;
    }

    // Check file type - must be .txt, .pdf, .doc, .docx or .zip
    const allowedTypes = [
      "application/pdf",
      "application/msword",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "application/zip",
      "application/x-zip-compressed",
      "application/x-zip",
      "text/plain",
    ];
    if (!allowedTypes.includes(file.type)) {
      alert("Only PDF, DOC, DOCX, ZIP and TXT files are allowed");
      return;
    }
    // Check file name - must not contain special characters
    const fileName = file.name;
    const regex = /^[a-zA-Z0-9_.-]+$/;
    if (!regex.test(fileName)) {
      alert("File name must not contain special characters");
      return;
    }

    const formData = new FormData();
    formData.append("exploitFile", file);

    try {
      const response = await fetch(config.BACKEND_URL + "/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const uploadedFile = await response.json();

        console.log("Exploit uploaded successfully:", uploadedFile);

        // Refresh the list of uploaded files
        refetch();
      } else {
        console.error("Exploit upload failed");
      }
    } catch (error) {
      console.error("Error uploading exploit:", error);
    }
  };

  if (loading) {
    return <p>Loading...</p>;
  }

  return (
    <div className="container py-5">
      <div className="text-center mb-5">
      <div className="glitch-logo">GlitchSnitch</div>
      <p className="lead">
        Share your exploits. Secure the world. Or just brag a little.
      </p>
      </div>

      <div
      className="glitch-box mx-auto"
      style={{
        maxWidth: "700px",
      }}
      >
      <h3 className="mb-3">Upload Your Exploits</h3>
      <p>
        Got a zero-day or a proof-of-concept? Upload it here and let the world
        (or just us) know about your genius. Remember, only the following file
        types are allowed: <strong>PDF, DOC, DOCX, ZIP and TXT</strong>. Also, keep it under 5MB.
      </p>
      <form
        id="uploadForm"
        onSubmit={handleSubmit}
        encType="multipart/form-data"
        className="mb-4"
      >
        <div className="mb-3">
        <input
          type="file"
          name="exploitFile"
          className="form-control"
          onChange={handleFileChange}
        />
        </div>
        <button
        type="submit"
        className="btn btn-outline-light btn-lg px-4 py-2 text-uppercase fw-bold text-light"
        >
        Upload Exploit
        </button>
      </form>

      <h4 className="mb-3">Uploaded Exploits</h4>
      <div id="fileList">
        {data && data.files.length > 0 ? (
        <ul className="list-group list-group-flush">
          {data.files.map((file, index) => (
          <li
            key={index}
            className="list-group-item bg-transparent text-light d-flex justify-content-between align-items-center"
          >
            <a
            href={fileDownloadURL(file)}
            rel="noopener noreferrer"
            className="text-cyber"
            >
            {file}
            </a>
            <a
            href={fileDownloadURL(file) + "?download=true"}
            target="_blank"
            className="btn btn-sm btn-outline-cyber"
            >
            Download
            </a>
          </li>
          ))}
        </ul>
        ) : (
        <p>No exploits uploaded yet.</p>
        )}
      </div>
      </div>

      <footer className="text-center mt-5">
      <small className="text-secondary">
        © 2025 GlitchSnitch LLC — "We may or may not be legally responsible."
      </small>
      </footer>
    </div>
  );
}
