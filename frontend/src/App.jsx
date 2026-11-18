import { useEffect, useState } from 'react'

const API = 'http://localhost:8000'

function Bar({ label, value, color }) {
  return (
    <div className="bar-row">
      <span className="bar-label">{label}</span>
      <div className="bar-track"><div className="bar-fill" style={{ width: `${value}%`, background: color }} /></div>
      <span className="bar-val">{value}</span>
    </div>
  )
}

function Chips({ items, cls }) {
  if (!items?.length) return <span className="muted">None</span>
  return <div className="chips">{items.map(s => <span key={s} className={`chip ${cls}`}>{s}</span>)}</div>
}

function RankingTable({ results, onView }) {
  return (
    <table>
      <thead><tr><th>#</th><th>Candidate</th><th>Experience</th><th>Match %</th><th>Matched Skills</th>{onView && <th></th>}</tr></thead>
      <tbody>
        {results.map(r => (
          <tr key={r.rank}>
            <td>{r.rank}</td><td>{r.name}{r.file_name && <div className="muted small">{r.file_name}</div>}</td>
            <td>{r.experience_years} yrs</td>
            <td><b className={r.scores.overall >= 70 ? 'good' : r.scores.overall >= 45 ? 'mid' : 'low'}>{r.scores.overall}%</b></td>
            <td>{r.matched_skills?.join(', ') || '—'}</td>
            {onView && <td><button onClick={() => onView(r)}>View</button></td>}
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default function App() {
  const [jdText, setJdText] = useState('')
  const [jdFile, setJdFile] = useState(null)
  const [files, setFiles] = useState([])
  const [data, setData] = useState(null)
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [runs, setRuns] = useState([])
  const [pastRun, setPastRun] = useState(null)

  async function loadHistory() {
    try {
      const res = await fetch(`${API}/api/history`)
      const json = await res.json()
      setRuns(json.runs || [])
    } catch { /* history is optional — ignore if the backend is down */ }
  }

  useEffect(() => { loadHistory() }, [])

  async function viewRun(id) {
    try {
      const res = await fetch(`${API}/api/history/${id}`)
      const json = await res.json()
      if (!json.error) {
        // Map stored rows onto the ranking-table shape (read-only view).
        setPastRun({
          ...json,
          results: json.results.map(r => ({
            rank: r.rank, name: r.name, experience_years: r.years, matched_skills: null,
            scores: { overall: r.overall, semantic: r.semantic, skill_coverage: r.skill_coverage, experience: r.experience_score },
          })),
        })
      }
    } catch { /* ignore */ }
  }

  async function runRanking() {
    setError(''); setLoading(true); setSelected(null)
    try {
      const fd = new FormData()
      fd.append('jd_text', jdText)
      if (jdFile) fd.append('jd_file', jdFile)
      files.forEach(f => fd.append('resumes', f))
      const res = await fetch(`${API}/api/rank`, { method: 'POST', body: fd })
      const json = await res.json()
      if (json.error) setError(json.error); else { setData(json); loadHistory() }
    } catch { setError('Could not reach the backend. Is it running on port 8000?') }
    setLoading(false)
  }

  return (
    <div className="page">
      <header>
        <h1>AI Resume Matching & Candidate Ranking</h1>
        <p className="sub">Paste a job description, upload resumes in batch, and get explainable AI match scores (0–100).</p>
      </header>

      <section className="card">
        <h2>1 · Job Description</h2>
        <textarea rows={8} placeholder="Paste the job description here…" value={jdText} onChange={e => setJdText(e.target.value)} />
        <label className="file-label">…or upload a JD file (.txt / .pdf / .docx)
          <input type="file" accept=".txt,.pdf,.docx" onChange={e => setJdFile(e.target.files[0])} />
        </label>
        {jdFile && <span className="muted"> Selected: {jdFile.name}</span>}
      </section>

      <section className="card">
        <h2>2 · Resumes (batch upload, PDF / DOCX)</h2>
        <div className="drop" onDragOver={e => e.preventDefault()}
             onDrop={e => { e.preventDefault(); setFiles([...e.dataTransfer.files]) }}>
          <p>Drag & drop resume files here, or</p>
          <input type="file" multiple accept=".pdf,.docx" onChange={e => setFiles([...e.target.files])} />
          {files.length > 0 && <p className="muted">{files.length} file(s) selected</p>}
        </div>
        <button className="primary" disabled={loading || files.length === 0 || (!jdText && !jdFile)} onClick={runRanking}>
          {loading ? 'Analysing…' : `Rank ${files.length || ''} Candidates`}
        </button>
        {error && <p className="error">{error}</p>}
      </section>

      {data && (
        <section className="card">
          <h2>3 · Ranking Dashboard</h2>
          <p className="muted">
            {data.total_candidates} candidates · JD skills detected: {data.jd_summary.skills.join(', ') || 'none'} ·
            Required experience: {data.jd_summary.required_years} years · Semantic method: <b>{data.semantic_method}</b>
          </p>
          <RankingTable results={data.results} onView={setSelected} />
        </section>
      )}

      {runs.length > 0 && (
        <section className="card">
          <h2>Past runs</h2>
          <p className="muted">Saved rankings from this device — click one to view its stored results.</p>
          {runs.map(run => (
            <button key={run.id} className="run-item" onClick={() => viewRun(run.id)}>
              <span>{new Date(run.created_at).toLocaleString()} · {run.candidate_count} candidates · {run.semantic_method}</span>
              <span>Top: <b>{run.top_candidate}</b> ({run.top_score}%)</span>
            </button>
          ))}
        </section>
      )}

      {pastRun && (
        <section className="card">
          <h2>Past run — {new Date(pastRun.created_at).toLocaleString()}</h2>
          <p className="muted">
            {pastRun.candidate_count} candidates · JD skills detected: {pastRun.jd_skills.join(', ') || 'none'} ·
            Required experience: {pastRun.required_years} years · Semantic method: <b>{pastRun.semantic_method}</b>
          </p>
          <RankingTable results={pastRun.results} />
          <button onClick={() => setPastRun(null)}>Close</button>
        </section>
      )}

      {selected && (
        <div className="modal-bg" onClick={() => setSelected(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <button className="close" onClick={() => setSelected(null)}>×</button>
            <h2>{selected.name} — {selected.scores.overall}% match</h2>
            <p className="muted">{selected.email || ''} {selected.phone ? '· ' + selected.phone : ''}</p>
            {selected.education?.length > 0 && <p><b>Education:</b> {selected.education.join(' · ')}</p>}
            <h3>Score breakdown</h3>
            <Bar label="Semantic similarity (45%)" value={selected.scores.semantic} color="#4f46e5" />
            <Bar label="Skill coverage (35%)" value={selected.scores.skill_coverage} color="#059669" />
            <Bar label="Experience (20%)" value={selected.scores.experience} color="#d97706" />
            <h3>Matched skills</h3><Chips items={selected.matched_skills} cls="ok" />
            <h3>Missing skills</h3><Chips items={selected.missing_skills} cls="miss" />
            <h3>Experience comparison</h3>
            <p>Candidate: {selected.experience_comparison.candidate_years} years · Required: {selected.experience_comparison.required_years} years ·
               {selected.experience_comparison.meets_requirement ? ' Meets the requirement ✓' : ' Below / not specified'}</p>
            <h3>Why this score?</h3>
            <ul>{selected.reasons.map((x, i) => <li key={i}>{x}</li>)}</ul>
            <h3>All skills found in resume</h3><Chips items={selected.candidate_skills} cls="" />
          </div>
        </div>
      )}
      <footer className="muted small">Prototype — uses synthetic/demo data only. Scoring: Overall = 0.45×Semantic + 0.35×Skill Coverage + 0.20×Experience.</footer>
    </div>
  )
}
