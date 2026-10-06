import React from 'react';
import { Check, CircleAlert, Sparkles } from 'lucide-react';

function ProgressBar({ label, value }) {
  return (
    <div className="score-row">
      <div><span>{label}</span><strong>{value}%</strong></div>
      <div className="score-track"><span style={{ width: `${value}%` }} /></div>
    </div>
  );
}

export default function MatchResults({ insights, scoreBreakdown, matchScore }) {
  const matched = insights?.matched || [];
  const missing = insights?.missing || [];
  const hasScore = Number.isFinite(matchScore);

  return (
    <section className="results-section animate-fadeIn" aria-live="polite">
      <div className="results-heading">
        <div>
          <p className="eyebrow">Your match</p>
          {hasScore ? (
            <div className="match-score"><strong>{matchScore}%</strong><span>{matchScore >= 80 ? 'Strong match' : matchScore >= 60 ? 'Promising match' : 'Room to grow'}</span></div>
          ) : (
            <h2>Here is what stands out</h2>
          )}
          <p className="results-summary">{hasScore ? 'Your resume aligns with the most important parts of this role.' : 'Review your strengths and the areas that may need more attention.'}</p>
          {insights?.experience_relevance?.summary && <p className="experience-summary">{insights.experience_relevance.summary}</p>}
        </div>
        <div className="results-badge"><Sparkles size={18} /><span>Ready to explore</span></div>
      </div>

      {hasScore && scoreBreakdown && (
        <div className="score-breakdown">
          {Object.entries(scoreBreakdown).map(([label, value]) => <ProgressBar key={label} label={label} value={value} />)}
        </div>
      )}

      {insights?.requirement_coverage !== undefined && (
        <div className="coverage-note"><strong>{insights.requirement_coverage}%</strong><span>of weighted job requirements are covered by your resume</span></div>
      )}

      <div className="result-columns">
        <div className="result-group">
          <h3><Check size={16} /> Your strengths</h3>
          <div className="result-pills">{matched.length ? matched.slice(0, 8).map((skill) => <span className="result-pill result-pill-good" key={skill}>{skill}</span>) : <p className="result-empty">No direct strengths found yet.</p>}</div>
          {matched.length > 8 && <button className="text-button">View all</button>}
        </div>
        <div className="result-group">
          <h3><CircleAlert size={16} /> Skill gaps</h3>
          <p className="result-helper">Skills from the role that are not clearly present in your resume.</p>
          <div className="result-pills">{missing.length ? missing.slice(0, 8).map((skill) => <span className="result-pill result-pill-gap" key={skill}>{skill}</span>) : <p className="result-empty">No clear gaps found.</p>}</div>
          {missing.length > 8 && <button className="text-button">View all</button>}
        </div>
      </div>
    </section>
  );
}
