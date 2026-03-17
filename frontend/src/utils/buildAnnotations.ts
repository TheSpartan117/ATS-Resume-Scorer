/**
 * Annotation builder — maps backend scoring issues to text highlights.
 *
 * Each annotation links a substring of the resume text to a category,
 * issue description, optional suggestion, and severity level.
 */

export interface Annotation {
  id: string
  text: string            // phrase to highlight in the resume
  category: string        // e.g. "Content Quality"
  issue: string           // full issue description
  suggestion?: string     // optional text explaining the suggestion
  replacement?: string    // the exact string to insert when applying the fix
  severity: 'critical' | 'warning' | 'suggestion'
  applied: boolean        // true once the user applies the fix
  startIndex: number      // position in resume text
  endIndex: number        // end position
}

interface CategoryScore {
  score: number
  maxScore: number
  issues?: string[]
}

interface Issues {
  critical: string[]
  warnings: string[]
  suggestions: string[]
}

// Category → highlight colour class (used by the viewer)
export const CATEGORY_COLORS: Record<string, string> = {
  'Keyword Matching': '#3b82f6',      // blue
  'Content Quality': '#f97316',       // orange
  'Format & Structure': '#8b5cf6',    // purple
  'Professional Polish': '#eab308',   // yellow
  'Experience Validation': '#06b6d4', // cyan
  'Red Flags': '#ef4444',             // red
  'Readability': '#14b8a6',           // teal
}

export const CATEGORY_BG_COLORS: Record<string, string> = {
  'Keyword Matching': 'rgba(59,130,246,0.18)',
  'Content Quality': 'rgba(249,115,22,0.18)',
  'Format & Structure': 'rgba(139,92,246,0.18)',
  'Professional Polish': 'rgba(234,179,8,0.18)',
  'Experience Validation': 'rgba(6,182,212,0.18)',
  'Red Flags': 'rgba(239,68,68,0.18)',
  'Readability': 'rgba(20,184,166,0.18)',
}

/**
 * Extract actionable phrases from an issue string.
 *
 * Pulls out quoted terms, terms after "overused:", missing keywords, weak verbs, etc.
 */
function extractPhrases(issue: string): string[] {
  const phrases: string[] = []

  // Quoted phrases: "agile", "managed"
  const quoted = issue.match(/"([^"]+)"/g)
  if (quoted) {
    quoted.forEach(q => phrases.push(q.replace(/"/g, '')))
  }

  // "overused: ..." pattern from repetition feedback
  const overused = issue.match(/overused:\s*(.+)$/i)
  if (overused) {
    overused[1].split(',').forEach(w => {
      const clean = w.trim().replace(/"/g, '')
      if (clean) phrases.push(clean)
    })
  }

  // "responsible for" pattern (weak verb)
  if (issue.toLowerCase().includes('responsible for')) {
    phrases.push('responsible for')
  }

  // "worked on" pattern
  if (issue.toLowerCase().includes("'worked'") || issue.toLowerCase().includes('"worked"')) {
    phrases.push('worked')
  }

  // "helped" pattern
  if (issue.toLowerCase().includes("'helped'") || issue.toLowerCase().includes('"helped"')) {
    phrases.push('helped')
  }

  return phrases
}

/**
 * Determine a suggestion and the actual replacement text based on the issue type.
 */
function getSuggestionForIssue(issue: string, phrase: string): { suggestion?: string, replacement?: string } {
  const lowerIssue = issue.toLowerCase()
  const lowerPhrase = phrase.toLowerCase()

  if (lowerIssue.includes('action verb') || lowerIssue.includes('passive') || lowerIssue.includes('weak')) {
    const replacements: Record<string, string> = {
      'responsible for': 'Led',
      'worked on': 'Developed',
      'worked': 'Delivered',
      'helped': 'Facilitated',
      'managed': 'Orchestrated',
      'did': 'Executed',
      'made': 'Engineered',
      'used': 'Leveraged',
    }
    const replacement = replacements[lowerPhrase] || 'Spearheaded' // fallback strong verb
    return {
      suggestion: `Replace "${phrase}" with a stronger action verb like "${replacement}"`,
      replacement
    }
  }

  if (lowerIssue.includes('repetit') || lowerIssue.includes('overused')) {
    const synonyms: Record<string, string[]> = {
      'product': ['solution', 'offering', 'platform', 'application', 'system'],
      'owned': ['directed', 'spearheaded', 'governed', 'piloted', 'steered'],
      'managed': ['orchestrated', 'guided', 'administered', 'supervised'],
      'led': ['championed', 'pioneered', 'headed', 'commanded'],
      'developed': ['architected', 'engineered', 'formulated', 'constructed'],
      'created': ['designed', 'established', 'instituted', 'forged'],
      'team': ['group', 'squad', 'unit', 'cohort', 'division'],
    }

    const options = synonyms[lowerPhrase]
    if (options && options.length > 0) {
      // Pick a random synonym based on phrase length to be pseudo-deterministic but varied
      const idx = phrase.length % options.length
      const suggestionVerb = options[idx]
      // Capitalize if original phrase was capitalized
      const replacement = phrase[0] === phrase[0].toUpperCase() 
        ? suggestionVerb.charAt(0).toUpperCase() + suggestionVerb.slice(1) 
        : suggestionVerb
      
      return {
        suggestion: `Consider replacing "${phrase}" with "${replacement}" to add variety`,
        replacement
      }
    }

    return {
      suggestion: `Consider replacing "${phrase}" with a synonym to add variety`,
      // fallback generic replacement - user might not want to apply this blindly but we give them something
      replacement: phrase + ' (synonym)' 
    }
  }

  return {}
}

/**
 * Build annotations by scanning the resume text for phrases mentioned in issues.
 */
export function buildAnnotations(
  resumeText: string,
  breakdown: Record<string, CategoryScore>,
  issues: Issues
): Annotation[] {
  const annotations: Annotation[] = []
  const usedRanges: Array<[number, number]> = []
  let idCounter = 0

  // Helper: check if a range overlaps with already-used ranges
  const overlaps = (start: number, end: number): boolean => {
    return usedRanges.some(([s, e]) => start < e && end > s)
  }

  const lowerText = resumeText.toLowerCase()

  // Process category issues from breakdown
  for (const [categoryName, category] of Object.entries(breakdown)) {
    if (!category.issues || category.issues.length === 0) continue

    for (const issue of category.issues) {
      const phrases = extractPhrases(issue)

      for (const phrase of phrases) {
        const lowerPhrase = phrase.toLowerCase()
        let searchFrom = 0

        // Find all occurrences of this phrase in the resume
        while (searchFrom < lowerText.length) {
          const idx = lowerText.indexOf(lowerPhrase, searchFrom)
          if (idx === -1) break

          const endIdx = idx + phrase.length
          if (!overlaps(idx, endIdx)) {
            const { suggestion, replacement } = getSuggestionForIssue(issue, phrase)
            annotations.push({
              id: `ann-${idCounter++}`,
              text: resumeText.substring(idx, endIdx),
              category: categoryName,
              issue,
              suggestion,
              replacement,
              severity: category.score === 0 ? 'critical' : 'warning',
              applied: false,
              startIndex: idx,
              endIndex: endIdx,
            })
            usedRanges.push([idx, endIdx])
          }
          searchFrom = endIdx
        }
      }
    }
  }

  // Also process global critical/warning issues that might not map to a specific category
  const severityMap: Array<[string[], 'critical' | 'warning' | 'suggestion']> = [
    [issues.critical, 'critical'],
    [issues.warnings, 'warning'],
    [issues.suggestions, 'suggestion'],
  ]

  for (const [issueList, severity] of severityMap) {
    for (const issue of issueList) {
      const phrases = extractPhrases(issue)
      for (const phrase of phrases) {
        const lowerPhrase = phrase.toLowerCase()
        let searchFrom = 0

        while (searchFrom < lowerText.length) {
          const idx = lowerText.indexOf(lowerPhrase, searchFrom)
          if (idx === -1) break

          const endIdx = idx + phrase.length
          if (!overlaps(idx, endIdx)) {
            // Try to infer category from issue text
            let category = 'General'
            const lowerIssue = issue.toLowerCase()
            if (lowerIssue.includes('keyword')) category = 'Keyword Matching'
            else if (lowerIssue.includes('verb') || lowerIssue.includes('quantif') || lowerIssue.includes('achievement')) category = 'Content Quality'
            else if (lowerIssue.includes('format') || lowerIssue.includes('page') || lowerIssue.includes('section')) category = 'Format & Structure'
            else if (lowerIssue.includes('grammar') || lowerIssue.includes('professional') || lowerIssue.includes('pronoun')) category = 'Professional Polish'
            else if (lowerIssue.includes('repetit') || lowerIssue.includes('gap') || lowerIssue.includes('hop')) category = 'Red Flags'
            else if (lowerIssue.includes('readab') || lowerIssue.includes('bullet') || lowerIssue.includes('passive')) category = 'Readability'

            const { suggestion, replacement } = getSuggestionForIssue(issue, phrase)

            annotations.push({
              id: `ann-${idCounter++}`,
              text: resumeText.substring(idx, endIdx),
              category,
              issue,
              suggestion,
              replacement,
              severity,
              applied: false,
              startIndex: idx,
              endIndex: endIdx,
            })
            usedRanges.push([idx, endIdx])
          }
          searchFrom = endIdx
        }
      }
    }
  }

  // Sort by startIndex for rendering order
  annotations.sort((a, b) => a.startIndex - b.startIndex)

  return annotations
}
