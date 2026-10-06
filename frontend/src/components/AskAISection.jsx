import React, { useState } from 'react';
import { ArrowRight, Sparkles } from 'lucide-react';
import toast from 'react-hot-toast';

const suggestions = [
  'What skills am I missing?',
  'Why is my match score low?',
  'Does my experience fit this role?',
  'How can I improve my resume?',
];

export default function AskAISection({ onAsk, isLoading, disabled }) {
  const [question, setQuestion] = useState('');

  const submit = (value) => {
    if (!value.trim()) {
      toast.error('Write a question first.');
      return;
    }
    onAsk(value.trim());
    setQuestion('');
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    submit(question);
  };

  return (
    <section className="ask-panel">
      <div className="ask-heading"><div className="ask-icon"><Sparkles size={18} /></div><div><p className="eyebrow">Ask AI</p><h2>Ask about your match</h2><p>Have a question about your resume or this job?</p></div></div>
      <form onSubmit={handleSubmit} className="ask-form">
        <input value={question} onChange={(event) => setQuestion(event.target.value)} disabled={disabled || isLoading} placeholder="e.g. What skills am I missing for this role?" aria-label="Question about your match" />
        <button type="submit" disabled={disabled || isLoading}><span>{isLoading ? 'Thinking...' : 'Ask AI'}</span><ArrowRight size={16} /></button>
      </form>
      <div className="suggestions"><span>Try asking</span>{suggestions.map((suggestion) => <button key={suggestion} onClick={() => submit(suggestion)} disabled={disabled || isLoading}>{suggestion}</button>)}</div>
    </section>
  );
}
