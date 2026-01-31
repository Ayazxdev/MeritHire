export const analyzeIntegrity = (testSession) => {
    const signals = [];
    let riskScore = 0;

    // --- 1. TIME ANOMALY DETECTION ---
    // Rule: Identifying superhuman speeds (e.g., answering code questions in < 3 seconds)
    const MIN_HUMAN_TIME_PER_QUESTION_MS = 4000; // 4 seconds
    const fastAnswers = testSession.interactions.filter(i => i.timeTaken < MIN_HUMAN_TIME_PER_QUESTION_MS);

    // If > 50% of questions were answered unnaturally fast
    if (fastAnswers.length > testSession.interactions.length * 0.5) {
        signals.push({
            type: "time_anomaly",
            severity: "high",
            details: "Completion speed exceeds cognitive verification threshold."
        });
        riskScore += 0.4;
    } else if (testSession.totalTime < (testSession.interactions.length * 5000)) {
        // Entire test too fast
        signals.push({
            type: "time_anomaly",
            severity: "low",
            details: "Overall velocity suggests skimming."
        });
        riskScore += 0.15;
    }

    // --- 2. PATTERN DETECTION ---
    // Rule: Checking for heuristic guessing (e.g., A, A, A, A)
    // This is useful only if questions are randomized, but even then, humans rarely pick 'A' 4 times in a row intentionally.
    const answers = testSession.interactions.map(i => i.selectedOptionIndex); // [0, 0, 0]

    // Check for uniform distribution (All Same)
    const isUniform = answers.every(v => v === answers[0]);
    if (isUniform && answers.length > 2) {
        signals.push({
            type: "pattern_detection",
            severity: "medium",
            details: "Uniform answer selection pattern detected."
        });
        riskScore += 0.3;
    }

    // --- 3. RESUME COHERENCE (SIMPLIFIED) ---
    // Rule: High Seniority Claim + Low Test Score = Suspicious (or just Unqualified)
    // In an anti-cheat context, we flag "Incoherent" if they claim "Expert" but fail basic checks instantly.
    // For this lightweight version, we check Score vs Level.
    const score = testSession.score; // 0-100
    const claimedLevel = testSession.level || 'Mid';

    if (claimedLevel === 'Senior' && score < 30) {
        signals.push({
            type: "coherence_mismatch",
            severity: "low",
            details: "Seniority claim diverges significantly from observed output."
        });
        riskScore += 0.1;
    }

    // --- AGGREGATION ---
    // Cap score at 1.0
    riskScore = Math.min(riskScore, 1.0);

    return {
        riskScore: Number(riskScore.toFixed(2)),
        signals,
        timestamp: new Date().toISOString()
    };
};
