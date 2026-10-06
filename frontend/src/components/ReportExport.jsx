import React from 'react';
import { Download, FileDown } from 'lucide-react';
import toast from 'react-hot-toast';

export default function ReportExport({ report }) {
  const handleDownload = () => {
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `jd-analyzer-report-${new Date().toISOString().slice(0, 10)}.json`;
    link.click();
    URL.revokeObjectURL(url);
    toast.success('Report downloaded.');
  };

  return (
    <section className="report-bar">
      <div className="report-copy">
        <FileDown size={18} />
        <div><strong>Keep a copy of your analysis</strong><span>Download your results, answers, and supporting evidence.</span></div>
      </div>
      <button className="button button-light" onClick={handleDownload} disabled={!report.resume}>
        <Download size={16} /> Export report
      </button>
    </section>
  );
}