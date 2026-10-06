import React, { useState } from 'react';
import { CheckCircle2, BriefcaseBusiness } from 'lucide-react';
import toast from 'react-hot-toast';
import { uploadJd, getErrorMessage } from '../services/api';

export default function JobDescriptionCard({ onSaveSuccess, isSaved, sessionId }) {
  const [jdText, setJdText]       = useState('');
  const [isSaving, setIsSaving]   = useState(false);
  const maxLength = 5000;

  const handleChange = (e) => {
    if (e.target.value.length <= maxLength) setJdText(e.target.value);
  };

  const handleSave = async () => {
    if (!jdText.trim()) {
      toast.error('Please paste a job description first.');
      return;
    }
    setIsSaving(true);
    const tid = toast.loading('Saving job description…');
    try {
      const result = await uploadJd(jdText, sessionId);
      toast.dismiss(tid);
      toast.success('Job description saved successfully.');
      onSaveSuccess({
        session_id: result.session_id,
        saved: true,
        summary: {
          ...result,
          words: jdText.trim().split(/\s+/).length,
        },
        skill_insights: result.skill_insights,
      });
    } catch (err) {
      toast.dismiss(tid);
      toast.error(getErrorMessage(err));
    } finally {
      setIsSaving(false);
    }
  };

  // When user edits after saving, mark as unsaved
  const handleTextChange = (e) => {
    handleChange(e);
    if (isSaved) onSaveSuccess({ session_id: sessionId, saved: false });
  };

  return (
    <section className="upload-card">
      <div className="upload-card-heading">
        <div><p className="eyebrow">This job</p><h2>Paste the job description</h2></div>
        <BriefcaseBusiness size={19} />
      </div>

      <textarea
        rows={7}
        value={jdText}
        onChange={handleTextChange}
        placeholder="Paste the job description or requirements here..."
        className="w-full resize-y rounded-xl border border-gray-200 px-4 py-3.5 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all duration-300 bg-gray-50/20 focus:bg-white leading-relaxed"
      />

      <div className="mt-3 flex items-center justify-between">
        <p className="text-xs text-gray-400">{jdText.trim() ? 'Ready to compare' : 'Add the role details to continue'}</p>

        {jdText.trim() && (
          <button
            onClick={handleSave}
            disabled={isSaving || isSaved}
            className="bg-black hover:bg-zinc-800 disabled:opacity-50 text-white text-xs font-semibold px-5 py-2.5 rounded-lg transition-all duration-200 active:scale-[0.98] flex items-center gap-2 cursor-pointer disabled:cursor-not-allowed shadow-sm hover:shadow-md"
          >
            {isSaving ? (
              <>
                <svg className="animate-spin h-3.5 w-3.5 text-white" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 100 16v-4l-3 3 3 3v-4a8 8 0 01-8-8z" />
                </svg>
                Saving…
              </>
            ) : isSaved ? 'Saved ✓' : 'Save job description'}
          </button>
        )}
      </div>
    </section>
  );
}
