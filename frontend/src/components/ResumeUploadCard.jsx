import React, { useRef, useState } from 'react';
import { UploadCloud, FileText, X, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import { uploadPdf, getErrorMessage } from '../services/api';

export default function ResumeUploadCard({ onUploadSuccess, uploadedFileName, sessionId }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragActive, setIsDragActive] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef(null);

  const accept = (file) => {
    if (file.type !== 'application/pdf') {
      toast.error('Only PDF files are supported.');
      return;
    }
    setSelectedFile(file);
  };

  const handleFileChange = (e) => { if (e.target.files?.[0]) accept(e.target.files[0]); };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    if (e.dataTransfer.files?.[0]) accept(e.dataTransfer.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    const tid = toast.loading('Indexing resume…');
    try {
      const result = await uploadPdf(selectedFile, sessionId);
      toast.dismiss(tid);
      toast.success('Resume ready!');
      onUploadSuccess({ filename: selectedFile.name, sessionId: result.session_id });
      setSelectedFile(null);
    } catch (err) {
      toast.dismiss(tid);
      toast.error(getErrorMessage(err));
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemove = () => {
    setSelectedFile(null);
    onUploadSuccess(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const formatSize = (bytes) => bytes < 1024 * 1024
    ? `${(bytes / 1024).toFixed(0)} KB`
    : `${(bytes / (1024 * 1024)).toFixed(1)} MB`;

  return (
    <section className="card animate-fade-up" style={{ animationDelay: '0.05s' }}>
      <div className="card-label">
        <span className="card-label-dot" />
        Step 1 — Your Resume
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />

      {/* Already uploaded */}
      {uploadedFileName && !selectedFile && (
        <div className="file-chip animate-fade-in" style={{ marginBottom: 0 }}>
          <div className="file-chip-icon success">
            <CheckCircle size={18} />
          </div>
          <div className="file-chip-body">
            <div className="file-chip-name">{uploadedFileName}</div>
            <div className="file-chip-meta">Indexed and ready</div>
          </div>
          <button className="file-chip-remove" onClick={() => onUploadSuccess(null)} aria-label="Clear">
            <X size={15} />
          </button>
        </div>
      )}

      {/* File selected, not yet uploaded */}
      {selectedFile && (
        <>
          <div className="file-chip animate-fade-in" style={{ marginBottom: 12 }}>
            <div className="file-chip-icon pending">
              <FileText size={18} />
            </div>
            <div className="file-chip-body">
              <div className="file-chip-name">{selectedFile.name}</div>
              <div className="file-chip-meta">{formatSize(selectedFile.size)} · PDF</div>
            </div>
            {!isUploading && (
              <button className="file-chip-remove" onClick={handleRemove} aria-label="Remove">
                <X size={15} />
              </button>
            )}
          </div>
          <button className="btn-primary" onClick={handleUpload} disabled={isUploading}>
            {isUploading ? (
              <>
                <span className="spinner" />
                Indexing…
              </>
            ) : 'Upload Resume'}
          </button>
        </>
      )}

      {/* Drop zone */}
      {!selectedFile && !uploadedFileName && (
        <div
          className={`drop-zone${isDragActive ? ' drag-active' : ''}`}
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current.click()}
        >
          <div className="drop-zone-icon">
            <UploadCloud size={22} strokeWidth={1.5} />
          </div>
          <div>
            <p className="drop-title">Drop your resume here or click to browse</p>
            <p className="drop-sub">PDF only · Max 10 MB</p>
          </div>
        </div>
      )}
    </section>
  );
}
