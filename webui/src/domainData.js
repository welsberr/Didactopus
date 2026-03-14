export const domains = [
  {
    id: "bayesian-reasoning",
    title: "Bayesian Reasoning",
    subtitle: "Probability, evidence, updating, and model criticism",
    level: "novice-friendly",
    concepts: [
      {
        id: "prior",
        title: "Prior",
        prerequisites: [],
        masteryDimension: "mastery",
        exerciseReward: "Prior badge earned"
      },
      {
        id: "posterior",
        title: "Posterior",
        prerequisites: ["prior"],
        masteryDimension: "mastery",
        exerciseReward: "Posterior path opened"
      },
      {
        id: "model-checking",
        title: "Model Checking",
        prerequisites: ["posterior"],
        masteryDimension: "mastery",
        exerciseReward: "Model-checking unlocked"
      }
    ],
    onboarding: {
      headline: "Start with a fast visible win",
      body: "Read one short orientation, answer one guided question, and leave with your first mastery marker.",
      checklist: [
        "Read the one-screen topic orientation",
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
    subtitle: "Descriptive statistics, sampling, and inference",
    level: "novice-friendly",
    concepts: [
      {
        id: "descriptive",
        title: "Descriptive Statistics",
        prerequisites: [],
        masteryDimension: "mastery",
        exerciseReward: "Descriptive tools unlocked"
      },
      {
        id: "sampling",
        title: "Sampling",
        prerequisites: ["descriptive"],
        masteryDimension: "mastery",
        exerciseReward: "Sampling pathway opened"
      },
      {
        id: "inference",
        title: "Inference",
        prerequisites: ["sampling"],
        masteryDimension: "mastery",
        exerciseReward: "Inference challenge unlocked"
      }
    ],
    onboarding: {
      headline: "Build your first useful data skill",
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
