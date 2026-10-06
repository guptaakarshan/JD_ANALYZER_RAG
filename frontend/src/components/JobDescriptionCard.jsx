import React, { useState } from 'react';
import { CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import { uploadJd, getErrorMessage } from '../services/api';

export default function JobDescriptionCard({ onSaveSuccess, isSaved, sessionId }) {
  const [jdText, setJdText] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const maxLength = 5000;

  const handleChange = (e) => {
    if (e.target.value.length <= maxLength) setJdText(e.target.value);
    if (isSaved) onSaveSuccess(false);
  };

  const handleSave = async () => {
    if (!jdText.trim()) {
      toast.error('Please paste a job description first.');
      return;
    }
    setIsSaving(true);
    const tid = toast.loading('Indexing job description…');
    try {
      const result = await uploadJd(jdText, sessionId);
      toast.dismiss(tid);
      toast.success('Job description ready!');
      onSaveSuccess(result.session_id);
    } catch (err) {
      toast.dismiss(tid);
      toast.error(getErrorMessage(err));
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <section className="card animate-fade-up" style={{ animationDelay: '0.1s' }}>
      <div className="card-label" style={{ justifyContent: 'space-between' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span className="card-label-dot" style={{ background: 'var(--accent-2)' }} />
          Step 2 — Job Description
        </span>
        {isSaved && (
          <span className="badge badge-green">
            <CheckCircle size={11} />
            Ready
          </span>
        )}
      </div>

      <textarea
        className="jd-textarea"
        rows={7}
        value={jdText}
        onChange={handleChange}
        placeholder="Paste the job description or requirements here…"
      />

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 10 }}>
        <span className="char-count">{jdText.length} / {maxLength}</span>
        {jdText.trim() && (
          <button
            className="btn-ghost"
            onClick={handleSave}
            disabled={isSaving || isSaved}
          >
            {isSaving ? (
              <>
                <span className="spinner" style={{ borderTopColor: 'var(--accent-2)', borderColor: 'rgba(99,102,241,0.25)', width: 13, height: 13 }} />
                Saving…
              </>
            ) : isSaved ? 'Saved ✓' : 'Save Job Description'}
          </button>
        )}
      </div>
    </section>
  );
}
