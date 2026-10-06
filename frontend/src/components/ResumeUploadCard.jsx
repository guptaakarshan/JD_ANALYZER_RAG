import React, { useRef, useState } from 'react';
import { UploadCloud, FileText, X, CheckCircle2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { uploadPdf, getErrorMessage } from '../services/api';

export default function ResumeUploadCard({ onUploadSuccess, uploadedFileName, sessionId }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragActive, setIsDragActive]  = useState(false);
  const [isUploading, setIsUploading]    = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
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
    const tid = toast.loading('Uploading resume…');
    try {
      const result = await uploadPdf(selectedFile, sessionId, (event) => {
        if (event.total) setUploadProgress(Math.round((event.loaded / event.total) * 100));
      });
      toast.dismiss(tid);
      toast.success('Resume uploaded successfully.');
      onUploadSuccess({
        filename: result.filename,
        session_id: result.session_id,
        summary: result,
        skill_insights: result.skill_insights,
      });
    } catch (err) {
      toast.dismiss(tid);
      toast.error(getErrorMessage(err));
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleRemove = () => {
    setSelectedFile(null);
    onUploadSuccess({ filename: null, session_id: null });
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <section className="upload-card">
      <div className="upload-card-heading"><div><p className="eyebrow">Your resume</p><h2>Upload your PDF resume</h2></div><FileText size={19} /></div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        className="hidden"
        onChange={handleFileChange}
      />

      {/* Already successfully uploaded */}
      {uploadedFileName && !selectedFile && (
        <div className="rounded-xl border border-green-100 bg-green-50/50 px-4 py-3.5 flex items-center gap-3 animate-fadeIn">
          <CheckCircle2 className="h-5 w-5 text-green-600 shrink-0" />
          <p className="text-sm font-medium text-green-800 truncate flex-1">{uploadedFileName}</p>
          <span className="upload-ready">Uploaded</span>
          <button
            onClick={() => onUploadSuccess({ filename: null, session_id: null })}
            className="text-green-500 hover:text-green-700 transition-colors shrink-0 p-1 hover:bg-green-100 rounded-full"
            aria-label="Clear upload"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* File selected but not yet uploaded */}
      {selectedFile && (
        <div className="rounded-xl border border-gray-100 bg-gray-50/50 px-4 py-3.5 flex items-center justify-between gap-3 mb-4 animate-fadeIn">
          <div className="flex items-center gap-3 min-w-0">
            <div className="bg-gray-100 rounded-lg p-2 shrink-0">
              <FileText className="h-5 w-5 text-gray-500" strokeWidth={1.5} />
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium text-gray-800 truncate">{selectedFile.name}</p>
              <p className="text-xs text-gray-400">{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</p>
            </div>
          </div>
          {!isUploading && (
            <button
              onClick={handleRemove}
              className="text-gray-400 hover:text-gray-600 shrink-0 transition-colors p-1 hover:bg-gray-200 rounded-full"
              aria-label="Remove file"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      )}

      {isUploading && (
        <div className="upload-progress" aria-live="polite">
          <div className="upload-progress-label"><span>Uploading resume</span><strong>{uploadProgress}%</strong></div>
          <div className="upload-progress-track"><span style={{ width: `${Math.max(uploadProgress, 4)}%` }} /></div>
        </div>
      )}

      {/* Drop zone — only shown when no file is staged and nothing has been uploaded */}
      {!selectedFile && !uploadedFileName && (
        <div
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current.click()}
          className={`cursor-pointer rounded-xl border-2 border-dashed py-12 flex flex-col items-center justify-center gap-4 transition-all duration-300 select-none ${
            isDragActive
              ? 'border-black bg-gray-50/50 scale-[1.01]'
              : 'border-gray-200 hover:border-gray-400 hover:bg-gray-50/50'
          }`}
        >
          <div className="bg-gray-50 rounded-full p-3 transition-colors duration-300">
            <UploadCloud className="h-8 w-8 text-gray-400" strokeWidth={1.5} />
          </div>
          <div className="text-center">
            <p className="text-sm font-medium text-gray-700">Click to upload or drag &amp; drop</p>
            <p className="text-xs text-gray-400 mt-1">PDF format · drag and drop supported</p>
          </div>
        </div>
      )}

      {/* Upload button */}
      {selectedFile && (
        <button
          onClick={handleUpload}
          disabled={isUploading}
          className="w-full bg-black hover:bg-zinc-800 disabled:opacity-50 text-white text-sm font-medium py-3 rounded-lg transition-all duration-200 active:scale-[0.99] flex items-center justify-center gap-2 shadow-sm hover:shadow-md cursor-pointer disabled:cursor-not-allowed"
        >
          {isUploading ? (
            <>
              <svg className="animate-spin h-4 w-4 text-white" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 100 16v-4l-3 3 3 3v-4a8 8 0 01-8-8z" />
              </svg>
              Uploading…
            </>
          ) : (
            'Upload resume'
          )}
        </button>
      )}
    </section>
  );
}
