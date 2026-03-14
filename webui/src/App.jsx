import React, { useMemo, useState } from "react";
import { domains } from "./sampleData";

function DomainCard({ domain, selected, onSelect }) {
  return (
    <button className={`domain-card ${selected ? "selected" : ""}`} onClick={() => onSelect(domain.id)}>
      <div className="domain-title">{domain.title}</div>
      <div className="domain-subtitle">{domain.subtitle}</div>
      <div className="domain-meta">
        <span>{domain.level}</span>
        <span>{domain.progress}% progress</span>
      </div>
    </button>
  );
}

function OnboardingPanel({ onboarding }) {
  return (
    <section className="card">
      <h2>First-session onboarding</h2>
      <h3>{onboarding.headline}</h3>
      <p>{onboarding.body}</p>
      <ul>
        {onboarding.checklist.map((item, idx) => <li key={idx}>{item}</li>)}
      </ul>
    </section>
  );
}

function NextStepCard({ step }) {
  return (
    <div className="step-card">
      <div className="step-header">
        <div>
          <h3>{step.title}</h3>
          <div className="muted">{step.minutes} minutes</div>
        </div>
        <div className="reward-pill">{step.reward}</div>
      </div>
      <p>{step.reason}</p>
      <details>
        <summary>Why this is recommended</summary>
        <ul>
          {step.why.map((item, idx) => <li key={idx}>{item}</li>)}
        </ul>
      </details>
      <button className="primary">Start this step</button>
    </div>
  );
}

function MasteryMap({ nodes }) {
  return (
    <section className="card">
      <h2>Visible mastery map</h2>
      <div className="map-grid">
        {nodes.map((node) => (
          <div key={node.id} className={`map-node ${node.status}`}>
            <div className="node-label">{node.label}</div>
            <div className="node-status">{node.status}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

function MilestonePanel({ milestones, rewardLabel, progress }) {
  return (
    <section className="card">
      <h2>Milestones and rewards</h2>
      <div className="progress-wrap">
        <div className="progress-label">Mastery progress</div>
        <div className="progress-bar"><div className="progress-fill" style={{ width: `${progress}%` }} /></div>
        <div className="muted">{progress}%</div>
      </div>
      <div className="reward-banner">{rewardLabel}</div>
      <ul>
        {milestones.map((m, idx) => <li key={idx}>{m}</li>)}
      </ul>
    </section>
  );
}

function CompliancePanel({ compliance }) {
  return (
    <section className="card">
      <h2>Source attribution and compliance</h2>
      <div className="compliance-grid">
        <div><strong>Sources</strong><br />{compliance.sources}</div>
        <div><strong>Attribution</strong><br />{compliance.attributionRequired ? "required" : "not required"}</div>
        <div><strong>Share-alike</strong><br />{compliance.shareAlikeRequired ? "yes" : "no"}</div>
        <div><strong>Noncommercial</strong><br />{compliance.noncommercialOnly ? "yes" : "no"}</div>
      </div>
      <div className="flag-row">
        {compliance.flags.length ? compliance.flags.map((f) => <span className="flag" key={f}>{f}</span>) : <span className="muted">No extra flags</span>}
      </div>
      <p className="muted">
        This panel is here so a learner or curator can inspect provenance-sensitive packs without needing to guess what the reuse constraints are.
      </p>
    </section>
  );
}

export default function App() {
  const [selectedDomainId, setSelectedDomainId] = useState(domains[0].id);
  const domain = useMemo(() => domains.find((d) => d.id === selectedDomainId) || domains[0], [selectedDomainId]);

  return (
    <div className="page">
      <header className="hero">
        <div>
          <h1>Didactopus learner prototype</h1>
          <p>
            Pick a topic, get a clear first session, see your mastery map, and understand why the system suggests each next step.
          </p>
        </div>
      </header>

      <section className="domain-grid">
        {domains.map((d) => (
          <DomainCard key={d.id} domain={d} selected={d.id === domain.id} onSelect={setSelectedDomainId} />
        ))}
      </section>

      <main className="layout">
        <div className="left-col">
          <OnboardingPanel onboarding={domain.onboarding} />
          <MasteryMap nodes={domain.masteryMap} />
        </div>

        <div className="center-col">
          <section className="card">
            <h2>What should I do next?</h2>
            <div className="steps-stack">
              {domain.nextSteps.map((step) => <NextStepCard key={step.id} step={step} />)}
            </div>
          </section>
        </div>

        <div className="right-col">
          <MilestonePanel milestones={domain.milestones} rewardLabel={domain.rewardLabel} progress={domain.progress} />
          <CompliancePanel compliance={domain.compliance} />
        </div>
      </main>
    </div>
  );
}
