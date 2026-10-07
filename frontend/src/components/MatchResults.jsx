import React, { useState } from 'react';
import {
  Check,
  CheckCircle2,
  AlertTriangle,
  Lightbulb,
  FolderGit2,
  GraduationCap,
  Briefcase,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

function ProgressBar({ label, value }) {
  if (value === undefined || value === null) return null;
  const pct = Math.min(100, Math.max(0, Math.round(value)));

  return (
    <div className="score-row">
      <div className="score-row-header">
        <span className="score-row-label">{label}</span>
        <span className="score-row-value">{pct}%</span>
      </div>
      <div className="score-track">
        <div
          className="score-fill"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export default function MatchResults({ analysis }) {
  const [showAllProjects, setShowAllProjects] = useState(false);

  if (!analysis) return null;

  const {
    overall_score = 0,
    match_label = 'Match Analysis',
    summary = '',
    breakdown = {},
    skills = {},
    strengths = [],
    gaps = [],
    relevant_projects = [],
    recommendations = [],
  } = analysis;

  const matchedSkills = skills?.matched || [];
  const missingRequired = skills?.missing_required || [];
  const missingPreferred = skills?.missing_preferred || [];
  const partialSkills = skills?.partial || [];

  // Relevance label helper
  const getRelevanceLabel = (rel) => {
    if (rel >= 75) return 'High relevance';
    if (rel >= 50) return 'Moderate relevance';
    return 'Relevant';
  };

  // Badge class based on score
  const getBadgeClass = (score) => {
    if (score >= 80) return 'badge-green';
    if (score >= 65) return 'badge-emerald';
    if (score >= 50) return 'badge-amber';
    return 'badge-subtle';
  };

  const displayedProjects = showAllProjects
    ? relevant_projects
    : relevant_projects.slice(0, 3);

  return (
    <div className="results-container animate-fade-up">
      {/* ─────────────────────────────────────────────────────────────────── */}
      {/* 1. OVERALL MATCH — HERO SECTION                                     */}
      {/* ─────────────────────────────────────────────────────────────────── */}
      <section className="match-hero-card">
        <div className="match-hero-header">
          <div>
            <div className="match-eyebrow">YOUR MATCH</div>
            <div className="match-hero-score-row">
              <span className="match-hero-score">{overall_score}%</span>
              <span className={`badge ${getBadgeClass(overall_score)}`}>
                {match_label}
              </span>
            </div>
          </div>
        </div>

        {summary && <p className="match-hero-summary">"{summary}"</p>}

        {/* Score Breakdown */}
        {breakdown && Object.keys(breakdown).length > 0 && (
          <div className="breakdown-wrap">
            <div className="breakdown-grid">
              <ProgressBar label="Required skills" value={breakdown.required_skills} />
              <ProgressBar label="Experience" value={breakdown.experience} />
              <ProgressBar label="Projects" value={breakdown.projects} />
              <ProgressBar label="Preferred skills" value={breakdown.preferred_skills} />
              {breakdown.education !== undefined && (
                <ProgressBar label="Education" value={breakdown.education} />
              )}
            </div>
          </div>
        )}
      </section>

      {/* ─────────────────────────────────────────────────────────────────── */}
      {/* 2 & 3. TWO-COLUMN: WHERE YOU STAND OUT / WHAT YOU MAY BE MISSING    */}
      {/* ─────────────────────────────────────────────────────────────────── */}
      <div className="results-grid-2">
        {/* WHERE YOU STAND OUT */}
        <section className="result-card">
          <div className="card-header-clean">
            <span className="card-title-clean">
              <CheckCircle2 size={16} className="text-emerald" />
              WHERE YOU STAND OUT
            </span>
          </div>

          {strengths.length > 0 ? (
            <ul className="strength-list">
              {strengths.slice(0, 4).map((s, idx) => (
                <li key={idx} className="strength-item">
                  <Check size={14} className="text-emerald shrink-0 mt-0.5" />
                  <span>{s}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="empty-hint">Direct experience aligns with target requirements.</p>
          )}

          {matchedSkills.length > 0 && (
            <div className="pill-group-wrap">
              <span className="pill-group-title">Matched skills:</span>
              <div className="pill-cloud">
                {matchedSkills.map((sk) => (
                  <span key={sk} className="skill-pill pill-matched">
                    {sk}
                  </span>
                ))}
              </div>
            </div>
          )}
        </section>

        {/* WHAT YOU MAY BE MISSING */}
        <section className="result-card">
          <div className="card-header-clean">
            <span className="card-title-clean">
              <AlertTriangle size={16} className="text-amber" />
              WHAT YOU MAY BE MISSING
            </span>
          </div>

          <div className="missing-groups">
            {/* High Priority (Missing Required) */}
            <div className="missing-subgroup">
              <span className="priority-label high">HIGH PRIORITY</span>
              {missingRequired.length > 0 ? (
                <div className="pill-cloud">
                  {missingRequired.map((sk) => (
                    <span key={sk} className="skill-pill pill-missing-req">
                      {sk}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="subtle-success">All required skills covered ✓</p>
              )}
            </div>

            {/* Good to have (Missing Preferred) */}
            <div className="missing-subgroup">
              <span className="priority-label good">GOOD TO HAVE</span>
              {missingPreferred.length > 0 ? (
                <div className="pill-cloud">
                  {missingPreferred.map((sk) => (
                    <span key={sk} className="skill-pill pill-missing-pref">
                      {sk}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="empty-hint">No preferred skill gaps</p>
              )}
            </div>

            {/* PARTIAL MATCHES */}
            {partialSkills.length > 0 && (
              <div className="missing-subgroup">
                <span className="priority-label partial">PARTIALLY MATCHED</span>
                <div className="pill-cloud">
                  {partialSkills.map((sk) => (
                    <span key={sk} className="skill-pill pill-partial">
                      {sk} <span className="pill-tag">Partial match</span>
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </section>
      </div>

      {/* ─────────────────────────────────────────────────────────────────── */}
      {/* 4 & 5. TWO-COLUMN: YOUR EXPERIENCE / PROJECTS                        */}
      {/* ─────────────────────────────────────────────────────────────────── */}
      <div className="results-grid-2">
        {/* YOUR EXPERIENCE */}
        <section className="result-card">
          <div className="card-header-clean">
            <span className="card-title-clean">
              <Briefcase size={16} className="text-zinc" />
              YOUR EXPERIENCE
            </span>
            {breakdown.experience !== undefined && (
              <span className="score-chip">{breakdown.experience}% fit</span>
            )}
          </div>

          <p className="section-body-text">
            {strengths.find((s) => s.toLowerCase().includes('intern') || s.toLowerCase().includes('experience') || s.toLowerCase().includes('engineering')) ||
              "Your background demonstrates practical software development experience relevant to the role's responsibilities."}
          </p>

          {/* Education subsection if meaningful */}
          {breakdown.education !== undefined && (
            <div className="edu-callout">
              <GraduationCap size={15} className="text-zinc shrink-0 mt-0.5" />
              <div>
                <span className="edu-title">EDUCATION FIT · {breakdown.education}%</span>
                <p className="edu-text">
                  Your degree credentials satisfy stated role requirements.
                </p>
              </div>
            </div>
          )}
        </section>

        {/* PROJECTS THAT STRENGTHEN YOUR APPLICATION */}
        <section className="result-card">
          <div className="card-header-clean">
            <span className="card-title-clean">
              <FolderGit2 size={16} className="text-zinc" />
              PROJECTS THAT STRENGTHEN YOUR APPLICATION
            </span>
          </div>

          {relevant_projects.length > 0 ? (
            <div className="projects-list">
              {displayedProjects.map((proj, idx) => (
                <div key={idx} className="project-item">
                  <div className="project-item-header">
                    <span className="project-name">{proj.name}</span>
                    <span className="project-relevance-chip">
                      {getRelevanceLabel(proj.relevance)}
                    </span>
                  </div>
                  {proj.reason && <p className="project-reason">"{proj.reason}"</p>}
                </div>
              ))}

              {relevant_projects.length > 3 && (
                <button
                  className="btn-link"
                  onClick={() => setShowAllProjects(!showAllProjects)}
                >
                  {showAllProjects ? (
                    <>Show less <ChevronUp size={13} /></>
                  ) : (
                    <>View {relevant_projects.length - 3} more projects <ChevronDown size={13} /></>
                  )}
                </button>
              )}
            </div>
          ) : (
            <p className="empty-hint">No dedicated projects listed in resume.</p>
          )}
        </section>
      </div>

      {/* ─────────────────────────────────────────────────────────────────── */}
      {/* 6 & 7. TWO-COLUMN: WHY YOU'RE A GOOD MATCH / HOW TO IMPROVE          */}
      {/* ─────────────────────────────────────────────────────────────────── */}
      <div className="results-grid-2">
        {/* WHY YOU'RE A GOOD MATCH */}
        <section className="result-card">
          <div className="card-header-clean">
            <span className="card-title-clean">
              <Check size={16} className="text-emerald" />
              WHY YOU'RE A GOOD MATCH
            </span>
          </div>

          <ul className="match-reasons-list">
            {strengths.slice(0, 4).map((str, idx) => (
              <li key={idx} className="reason-item">
                <span className="check-bullet">✓</span>
                <span>{str}</span>
              </li>
            ))}
          </ul>
        </section>

        {/* HOW TO IMPROVE YOUR MATCH */}
        <section className="result-card">
          <div className="card-header-clean">
            <span className="card-title-clean">
              <Lightbulb size={16} className="text-amber" />
              HOW TO IMPROVE YOUR MATCH
            </span>
          </div>

          {recommendations.length > 0 ? (
            <ol className="recommendation-list">
              {recommendations.slice(0, 4).map((rec, idx) => (
                <li key={idx} className="rec-item">
                  <span className="rec-number">{idx + 1}</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ol>
          ) : gaps.length > 0 ? (
            <ul className="recommendation-list">
              {gaps.slice(0, 3).map((g, idx) => (
                <li key={idx} className="rec-item">
                  <span className="rec-number">•</span>
                  <span>Address coverage for: {g}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="empty-hint">Your resume already shows strong alignment across key criteria.</p>
          )}
        </section>
      </div>
    </div>
  );
}
