import React, { useRef } from 'react';
import './UploadSection.css';

function UploadSection({ onUpload, uploading }) {
  const inputRef = useRef(null);

  const handleChange = (e) => {
    const file = e.target.files?.[0];
    if (file) onUpload(file);
    e.target.value = '';
  };

  return (
    <section className="upload-section">
      <h2>Upload JSON</h2>
      <div className="upload-box">
        <input
          ref={inputRef}
          type="file"
          accept=".json,application/json"
          onChange={handleChange}
          disabled={uploading}
          className="upload-input"
          id="file-upload"
        />
        <label htmlFor="file-upload" className="upload-label">
          {uploading ? 'Uploading…' : 'Choose a JSON file'}
        </label>
        <p className="upload-hint">Banking transaction JSON files only. Duplicate files are rejected.</p>
      </div>
    </section>
  );
}

export default UploadSection;
