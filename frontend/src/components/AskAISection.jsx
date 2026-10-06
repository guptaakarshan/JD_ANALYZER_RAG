import React, { useState } from 'react';
import { Sparkles, ArrowRight } from 'lucide-react';
import toast from 'react-hot-toast';

const SUGGESTIONS = [
  'What skills am I missing?',
  'Does my experience fit this role?',
  'How can I improve my resume?',
  'What are my strongest qualifications?',
];

export default function AskAISection({ onAsk, isLoading, disabled }) {
  const [question, setQuestion] = useState('');

  const submit = (value) => {
    if (!value.trim()) { toast.error('Write a question first.'); return; }
    onAsk(value.trim());
    setQuestion('');
  };

  const handleSubmit = (e) => { e.preventDefault(); submit(question); };

  return (
    <section className="ask-section animate-fade-up" style={{ animationDelay: '0.15s' }}>
      <div className="ask-header">
        <div className="ask-icon-wrap">
          <Sparkles size={18} />
        </div>
        <div>
          <p className="ask-title">Ask AI</p>
          <p className="ask-subtitle">Get personalized insights about your resume and this role.</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="ask-form-wrap">
        <div className="ask-input-row">
          <input
            className="ask-input"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={disabled || isLoading}
            placeholder="e.g. What skills am I missing for this role?"
            aria-label="Question about your match"
          />
          <button type="submit" className="ask-submit" disabled={disabled || isLoading}>
            {isLoading ? (
              <span className="spinner" />
            ) : (
              <>Ask AI <ArrowRight size={15} /></>
            )}
          </button>
        </div>
      </form>

      <div className="suggestions-wrap">
        <span className="suggestion-label">Try:</span>
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            className="suggestion-chip"
            onClick={() => submit(s)}
            disabled={disabled || isLoading}
          >
            {s}
          </button>
        ))}
      </div>
    </section>
  );
}
