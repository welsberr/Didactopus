export const domains = [
  {
    id: "bayesian-reasoning",
    title: "Bayesian Reasoning",
    subtitle: "Probability, evidence, updating, and model criticism",
    level: "novice-friendly",
    rewardLabel: "First prior unlocked",
    progress: 38,
    milestones: ["First concept mastered", "Posterior comparison unlocked"],
    masteryMap: [
      { id: "prior", label: "Prior", status: "mastered" },
      { id: "posterior", label: "Posterior", status: "active" },
      { id: "model-checking", label: "Model Checking", status: "locked" }
    ],
    nextSteps: [
      {
        id: "compare-prior-posterior",
        title: "Compare prior and posterior beliefs",
        reason: "You already showed solid understanding of priors, so the next high-value step is updating beliefs with evidence.",
        why: [
          "Prerequisite concepts are satisfied",
          "Your confidence on prior knowledge is above threshold",
          "This concept unlocks model-checking later"
        ],
        minutes: 18,
        reward: "Unlock model-checking pathway"
      },
      {
        id: "reinforce-prior-explanation",
        title: "Reinforce your explanation of priors",
        reason: "Your score is good, but confidence is still a little thin.",
        why: [
          "Confidence estimate below reinforcement target",
          "A short explanation exercise can stabilize recall"
        ],
        minutes: 8,
        reward: "Increase confidence ring"
      }
    ],
    onboarding: {
      headline: "Start with a fast visible win",
      body: "In your first session, you will read one short orientation, answer one guided question, and leave with your first mastery marker.",
      checklist: [
        "Read the one-screen orientation",
        "Answer one guided exercise",
        "Write one explanation in your own words"
      ]
    },
    compliance: {
      sources: 2,
      attributionRequired: true,
      shareAlikeRequired: true,
      noncommercialOnly: true,
      flags: ["share-alike", "noncommercial", "excluded-third-party-content"]
    }
  },
  {
    id: "intro-stats",
    title: "Introductory Statistics",
    subtitle: "Descriptive statistics, inference, and basic modeling",
    level: "novice-friendly",
    rewardLabel: "Variance trail opened",
    progress: 12,
    milestones: ["Orientation complete"],
    masteryMap: [
      { id: "descriptive", label: "Descriptive Stats", status: "active" },
      { id: "sampling", label: "Sampling", status: "locked" },
      { id: "inference", label: "Inference", status: "locked" }
    ],
    nextSteps: [
      {
        id: "descriptive-stats-basics",
        title: "Practice mean, median, and spread",
        reason: "This is the best low-friction entry point and gives immediate payoff.",
        why: [
          "No prerequisites are required",
          "It anchors later concepts in inference"
        ],
        minutes: 15,
        reward: "Unlock sampling"
      }
    ],
    onboarding: {
      headline: "Build your first useful tool",
      body: "You will learn one concept that immediately helps you summarize real data.",
      checklist: [
        "See one worked example",
        "Compute one short example yourself",
        "Explain what the result means"
      ]
    },
    compliance: {
      sources: 1,
      attributionRequired: true,
      shareAlikeRequired: false,
      noncommercialOnly: false,
      flags: []
    }
  }
];
