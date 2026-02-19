/**
 * Live Resume Editor with 50/50 split - Form fields on left, live preview on right
 */
import React, { useState, useEffect, useRef } from 'react';
import type { ScoreResult } from '../types/resume';

interface ResumeEditorLiveProps {
  value: string;
  onChange: (html: string) => void;
  currentScore: ScoreResult | null;
  isRescoring: boolean;
  wordCount: number;
  onRescore: () => void;
}

interface ResumeData {
  name: string;
  email: string;
  phone: string;
  location: string;
  linkedin: string;
  website: string;
  summary: string;
  experience: ExperienceItem[];
  education: EducationItem[];
  skills: string;
}

interface ExperienceItem {
  title: string;
  company: string;
  location: string;
  dates: string;
  description: string;
}

interface EducationItem {
  degree: string;
  institution: string;
  location: string;
  graduationDate: string;
  gpa: string;
}

/**
 * Parse HTML content to extract structured resume data
 */
const parseResumeHTML = (html: string): ResumeData => {
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, 'text/html');

  // Helper to get text content after a label
  const getTextAfterLabel = (label: string): string => {
    const strongTags = doc.querySelectorAll('strong');
    for (const strong of Array.from(strongTags)) {
      if (strong.textContent?.includes(label)) {
        const parent = strong.parentElement;
        if (parent) {
          return parent.textContent?.replace(`${label}:`, '').trim() || '';
        }
      }
    }
    return '';
  };

  // Extract contact info
  const name = getTextAfterLabel('Name');
  const email = getTextAfterLabel('Email');
  const phone = getTextAfterLabel('Phone');
  const location = getTextAfterLabel('Location');
  const linkedin = getTextAfterLabel('LinkedIn');
  const website = getTextAfterLabel('Website');

  // Extract summary (text after Professional Summary h2 and before next h2)
  let summary = '';
  const headers = doc.querySelectorAll('h2');
  for (let i = 0; i < headers.length; i++) {
    if (headers[i].textContent?.includes('Professional Summary')) {
      let nextElement = headers[i].nextElementSibling;
      const summaryParts: string[] = [];
      while (nextElement && nextElement.tagName !== 'H2') {
        if (nextElement.tagName === 'P' && !nextElement.textContent?.includes('Edit this section')) {
          summaryParts.push(nextElement.textContent || '');
        }
        nextElement = nextElement.nextElementSibling;
      }
      summary = summaryParts.join('\n');
      break;
    }
  }

  // Extract experience sections
  const experience: ExperienceItem[] = [];
  for (let i = 0; i < headers.length; i++) {
    if (headers[i].textContent?.includes('Experience')) {
      let nextElement = headers[i].nextElementSibling;
      let currentExp: Partial<ExperienceItem> = {};

      while (nextElement && nextElement.tagName !== 'H2') {
        if (nextElement.tagName === 'P') {
          const text = nextElement.textContent || '';
          const html = nextElement.innerHTML || '';

          if (html.includes('<strong>') && !text.includes('Edit this section')) {
            // Job title
            if (Object.keys(currentExp).length > 0) {
              experience.push(currentExp as ExperienceItem);
              currentExp = {};
            }
            currentExp.title = text;
          } else if (html.includes('<em>')) {
            // Company and location
            const parts = text.split(',');
            currentExp.company = parts[0]?.trim() || '';
            currentExp.location = parts[1]?.trim() || '';
          } else if (text.includes('-') && text.length < 50) {
            // Dates
            currentExp.dates = text;
          } else if (!text.includes('Edit this section')) {
            // Description
            currentExp.description = (currentExp.description || '') + text + '\n';
          }
        } else if (nextElement.tagName === 'BR' && Object.keys(currentExp).length > 0) {
          experience.push(currentExp as ExperienceItem);
          currentExp = {};
        }
        nextElement = nextElement.nextElementSibling;
      }

      if (Object.keys(currentExp).length > 0) {
        experience.push(currentExp as ExperienceItem);
      }
      break;
    }
  }

  // Extract education sections
  const education: EducationItem[] = [];
  for (let i = 0; i < headers.length; i++) {
    if (headers[i].textContent?.includes('Education')) {
      let nextElement = headers[i].nextElementSibling;
      let currentEdu: Partial<EducationItem> = {};

      while (nextElement && nextElement.tagName !== 'H2') {
        if (nextElement.tagName === 'P') {
          const text = nextElement.textContent || '';
          const html = nextElement.innerHTML || '';

          if (html.includes('<strong>') && !text.includes('Edit this section')) {
            // Degree
            if (Object.keys(currentEdu).length > 0) {
              education.push(currentEdu as EducationItem);
              currentEdu = {};
            }
            currentEdu.degree = text;
          } else if (html.includes('<em>')) {
            // Institution and location
            const parts = text.split(',');
            currentEdu.institution = parts[0]?.trim() || '';
            currentEdu.location = parts[1]?.trim() || '';
          } else if (text.includes('Graduated:')) {
            currentEdu.graduationDate = text.replace('Graduated:', '').trim();
          } else if (text.includes('GPA:')) {
            currentEdu.gpa = text.replace('GPA:', '').trim();
          }
        } else if (nextElement.tagName === 'BR' && Object.keys(currentEdu).length > 0) {
          education.push(currentEdu as EducationItem);
          currentEdu = {};
        }
        nextElement = nextElement.nextElementSibling;
      }

      if (Object.keys(currentEdu).length > 0) {
        education.push(currentEdu as EducationItem);
      }
      break;
    }
  }

  // Extract skills
  let skills = '';
  for (let i = 0; i < headers.length; i++) {
    if (headers[i].textContent?.includes('Skills')) {
      let nextElement = headers[i].nextElementSibling;
      while (nextElement && nextElement.tagName !== 'H2') {
        if (nextElement.tagName === 'P' && !nextElement.textContent?.includes('Edit this section')) {
          skills = nextElement.textContent || '';
          break;
        }
        nextElement = nextElement.nextElementSibling;
      }
      break;
    }
  }

  // Ensure at least one experience and education entry
  if (experience.length === 0) {
    experience.push({ title: '', company: '', location: '', dates: '', description: '' });
  }
  if (education.length === 0) {
    education.push({ degree: '', institution: '', location: '', graduationDate: '', gpa: '' });
  }

  return {
    name,
    email,
    phone,
    location,
    linkedin,
    website,
    summary,
    experience,
    education,
    skills
  };
};

/**
 * Convert structured data back to HTML
 */
const convertToHTML = (data: ResumeData): string => {
  const parts: string[] = [];

  // Contact Info Section
  parts.push('<h1>Contact Information</h1>');
  if (data.name) parts.push(`<p><strong>Name:</strong> ${data.name}</p>`);
  if (data.email) parts.push(`<p><strong>Email:</strong> ${data.email}</p>`);
  if (data.phone) parts.push(`<p><strong>Phone:</strong> ${data.phone}</p>`);
  if (data.location) parts.push(`<p><strong>Location:</strong> ${data.location}</p>`);
  if (data.linkedin) parts.push(`<p><strong>LinkedIn:</strong> ${data.linkedin}</p>`);
  if (data.website) parts.push(`<p><strong>Website:</strong> ${data.website}</p>`);

  // Professional Summary Section
  parts.push('<h2>Professional Summary</h2>');
  if (data.summary) {
    const summaryLines = data.summary.split('\n').filter(line => line.trim());
    summaryLines.forEach(line => parts.push(`<p>${line}</p>`));
  } else {
    parts.push('<p>Edit this section to add your professional summary...</p>');
  }

  // Experience Section
  parts.push('<h2>Experience</h2>');
  if (data.experience.some(exp => exp.title || exp.company || exp.description)) {
    data.experience.forEach((exp) => {
      if (exp.title) parts.push(`<p><strong>${exp.title}</strong></p>`);
      if (exp.company || exp.location) {
        const companyLocation = [exp.company, exp.location].filter(Boolean).join(', ');
        parts.push(`<p><em>${companyLocation}</em></p>`);
      }
      if (exp.dates) parts.push(`<p>${exp.dates}</p>`);
      if (exp.description) {
        const descLines = exp.description.split('\n').filter(line => line.trim());
        descLines.forEach(line => parts.push(`<p>${line}</p>`));
      }
      parts.push('<br>');
    });
  } else {
    parts.push('<p>Edit this section to add your work experience...</p>');
  }

  // Education Section
  parts.push('<h2>Education</h2>');
  if (data.education.some(edu => edu.degree || edu.institution)) {
    data.education.forEach((edu) => {
      if (edu.degree) parts.push(`<p><strong>${edu.degree}</strong></p>`);
      if (edu.institution || edu.location) {
        const institutionLocation = [edu.institution, edu.location].filter(Boolean).join(', ');
        parts.push(`<p><em>${institutionLocation}</em></p>`);
      }
      if (edu.graduationDate) parts.push(`<p>Graduated: ${edu.graduationDate}</p>`);
      if (edu.gpa) parts.push(`<p>GPA: ${edu.gpa}</p>`);
      parts.push('<br>');
    });
  } else {
    parts.push('<p>Edit this section to add your education...</p>');
  }

  // Skills Section
  parts.push('<h2>Skills</h2>');
  if (data.skills) {
    parts.push(`<p>${data.skills}</p>`);
  } else {
    parts.push('<p>Edit this section to add your skills...</p>');
  }

  return parts.join('\n');
};

/**
 * Parse issues to extract missing and present keywords
 */
const parseKeywordSuggestions = (score: ScoreResult | null): { missing: string[], present: string[] } => {
  if (!score) return { missing: [], present: [] };

  const missing: string[] = [];
  const present: string[] = [];

  // Check all issue types for keyword mentions
  const allIssues = [
    ...(score.issues.critical || []),
    ...(score.issues.warnings || []),
    ...(score.issues.suggestions || [])
  ];

  allIssues.forEach(issue => {
    const lowerIssue = issue.toLowerCase();

    // Extract missing keywords
    if (lowerIssue.includes('missing') || lowerIssue.includes('add')) {
      // Try to extract keywords from patterns like "Missing required keywords: python, docker"
      const keywordMatch = issue.match(/(?:keywords?|skills?)[:\s]+([a-zA-Z0-9,\s]+)/i);
      if (keywordMatch) {
        const keywords = keywordMatch[1].split(',').map(k => k.trim()).filter(Boolean);
        missing.push(...keywords);
      }
    }
  });

  // Extract present keywords from strengths
  if (score.strengths) {
    score.strengths.forEach(strength => {
      const lowerStrength = strength.toLowerCase();
      if (lowerStrength.includes('keyword') || lowerStrength.includes('skill')) {
        const keywordMatch = strength.match(/(?:keywords?|skills?)[:\s]+([a-zA-Z0-9,\s]+)/i);
        if (keywordMatch) {
          const keywords = keywordMatch[1].split(',').map(k => k.trim()).filter(Boolean);
          present.push(...keywords);
        }
      }
    });
  }

  return { missing: [...new Set(missing)], present: [...new Set(present)] };
};

export const ResumeEditorLive: React.FC<ResumeEditorLiveProps> = ({
  value,
  onChange,
  currentScore,
  isRescoring,
  wordCount
}) => {
  const [resumeData, setResumeData] = useState<ResumeData>({
    name: '',
    email: '',
    phone: '',
    location: '',
    linkedin: '',
    website: '',
    summary: '',
    experience: [{ title: '', company: '', location: '', dates: '', description: '' }],
    education: [{ degree: '', institution: '', location: '', graduationDate: '', gpa: '' }],
    skills: ''
  });

  const isInitializedRef = useRef(false);

  // Parse HTML on initial load
  useEffect(() => {
    if (value && !isInitializedRef.current) {
      const parsed = parseResumeHTML(value);
      setResumeData(parsed);
      isInitializedRef.current = true;
    }
  }, [value]);

  // Update HTML when data changes
  const updateData = (newData: ResumeData) => {
    setResumeData(newData);
    const html = convertToHTML(newData);
    onChange(html);
  };

  const addExperience = () => {
    updateData({
      ...resumeData,
      experience: [...resumeData.experience, { title: '', company: '', location: '', dates: '', description: '' }]
    });
  };

  const removeExperience = (index: number) => {
    if (resumeData.experience.length > 1) {
      updateData({
        ...resumeData,
        experience: resumeData.experience.filter((_, i) => i !== index)
      });
    }
  };

  const updateExperience = (index: number, field: keyof ExperienceItem, value: string) => {
    const newExperience = [...resumeData.experience];
    newExperience[index] = { ...newExperience[index], [field]: value };
    updateData({ ...resumeData, experience: newExperience });
  };

  const addEducation = () => {
    updateData({
      ...resumeData,
      education: [...resumeData.education, { degree: '', institution: '', location: '', graduationDate: '', gpa: '' }]
    });
  };

  const removeEducation = (index: number) => {
    if (resumeData.education.length > 1) {
      updateData({
        ...resumeData,
        education: resumeData.education.filter((_, i) => i !== index)
      });
    }
  };

  const updateEducation = (index: number, field: keyof EducationItem, value: string) => {
    const newEducation = [...resumeData.education];
    newEducation[index] = { ...newEducation[index], [field]: value };
    updateData({ ...resumeData, education: newEducation });
  };

  const keywordSuggestions = parseKeywordSuggestions(currentScore);

  return (
    <div className="flex h-full w-full overflow-hidden bg-gray-50">
      {/* Compact Top Bar - 60px */}
      {currentScore && (
        <div className="absolute top-0 left-0 right-0 h-[60px] bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 flex items-center justify-between shadow-md z-10">
          {/* Left: Score Circle */}
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <svg className="w-12 h-12" viewBox="0 0 120 120">
                  <circle cx="60" cy="60" r="54" fill="none" stroke="rgba(255,255,255,0.2)" strokeWidth="6" />
                  <circle
                    cx="60"
                    cy="60"
                    r="54"
                    fill="none"
                    stroke="white"
                    strokeWidth="6"
                    strokeDasharray={`${(currentScore.overallScore / 100) * 339.292} 339.292`}
                    transform="rotate(-90 60 60)"
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-lg font-bold text-white">{currentScore.overallScore}</span>
                </div>
              </div>
              <div>
                <div className="text-xs text-blue-100">Overall Score</div>
                <div className="text-sm font-semibold">{wordCount} words</div>
              </div>
            </div>

            {/* Issue Counts */}
            <div className="flex items-center space-x-4 ml-4">
              {currentScore.issues.critical && currentScore.issues.critical.length > 0 && (
                <div className="flex items-center space-x-1 bg-red-500 bg-opacity-30 px-3 py-1 rounded-full">
                  <span className="text-xl">🚨</span>
                  <span className="font-bold">{currentScore.issues.critical.length}</span>
                  <span className="text-xs">Critical</span>
                </div>
              )}
              {currentScore.issues.warnings && currentScore.issues.warnings.length > 0 && (
                <div className="flex items-center space-x-1 bg-yellow-500 bg-opacity-30 px-3 py-1 rounded-full">
                  <span className="text-xl">⚠️</span>
                  <span className="font-bold">{currentScore.issues.warnings.length}</span>
                  <span className="text-xs">Warnings</span>
                </div>
              )}
              {currentScore.issues.suggestions && currentScore.issues.suggestions.length > 0 && (
                <div className="flex items-center space-x-1 bg-blue-500 bg-opacity-30 px-3 py-1 rounded-full">
                  <span className="text-xl">💡</span>
                  <span className="font-bold">{currentScore.issues.suggestions.length}</span>
                  <span className="text-xs">Suggestions</span>
                </div>
              )}
            </div>
          </div>

          {/* Right: Mode indicator */}
          <div className="text-xs font-semibold text-blue-100">
            {currentScore.mode === 'ats_simulation' ? '🎯 ATS Mode' : '📝 Coach Mode'}
            {isRescoring && <span className="ml-2 animate-pulse">Updating...</span>}
          </div>
        </div>
      )}

      {/* Main Split Area - 50/50 */}
      <div className="flex w-full h-full" style={{ marginTop: '60px' }}>
        {/* LEFT 50% - Form Fields */}
        <div className="w-1/2 overflow-y-auto bg-white border-r border-gray-300">
          <div className="p-6 space-y-6">
            <h2 className="text-xl font-bold text-gray-800 border-b-2 border-blue-600 pb-2">Edit Resume</h2>

            {/* Contact Information */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-gray-700">Contact Information</h3>
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">Name</label>
                <input
                  type="text"
                  value={resumeData.name}
                  onChange={(e) => updateData({ ...resumeData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="John Doe"
                />
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Email</label>
                  <input
                    type="email"
                    value={resumeData.email}
                    onChange={(e) => updateData({ ...resumeData, email: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="john@example.com"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Phone</label>
                  <input
                    type="tel"
                    value={resumeData.phone}
                    onChange={(e) => updateData({ ...resumeData, phone: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="(555) 123-4567"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Location</label>
                  <input
                    type="text"
                    value={resumeData.location}
                    onChange={(e) => updateData({ ...resumeData, location: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="New York, NY"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">LinkedIn</label>
                  <input
                    type="text"
                    value={resumeData.linkedin}
                    onChange={(e) => updateData({ ...resumeData, linkedin: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="linkedin.com/in/johndoe"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Website</label>
                  <input
                    type="text"
                    value={resumeData.website}
                    onChange={(e) => updateData({ ...resumeData, website: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="johndoe.com"
                  />
                </div>
              </div>
            </div>

            {/* Professional Summary */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-gray-700">Professional Summary</h3>
              <textarea
                value={resumeData.summary}
                onChange={(e) => updateData({ ...resumeData, summary: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[100px]"
                placeholder="Experienced software engineer with 5+ years in web development..."
              />
            </div>

            {/* Experience */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-700">Experience</h3>
                <button
                  onClick={addExperience}
                  className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                >
                  + Add Experience
                </button>
              </div>
              {resumeData.experience.map((exp, index) => (
                <div key={index} className="p-4 bg-gray-50 rounded border border-gray-200 space-y-2">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-500">Experience #{index + 1}</span>
                    {resumeData.experience.length > 1 && (
                      <button
                        onClick={() => removeExperience(index)}
                        className="text-red-600 text-sm hover:text-red-800"
                      >
                        Remove
                      </button>
                    )}
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Job Title</label>
                    <input
                      type="text"
                      value={exp.title}
                      onChange={(e) => updateExperience(index, 'title', e.target.value)}
                      className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Senior Software Engineer"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">Company</label>
                      <input
                        type="text"
                        value={exp.company}
                        onChange={(e) => updateExperience(index, 'company', e.target.value)}
                        className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Tech Corp"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">Location</label>
                      <input
                        type="text"
                        value={exp.location}
                        onChange={(e) => updateExperience(index, 'location', e.target.value)}
                        className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="San Francisco, CA"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Dates</label>
                    <input
                      type="text"
                      value={exp.dates}
                      onChange={(e) => updateExperience(index, 'dates', e.target.value)}
                      className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Jan 2020 - Present"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Description</label>
                    <textarea
                      value={exp.description}
                      onChange={(e) => updateExperience(index, 'description', e.target.value)}
                      className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[80px]"
                      placeholder="Led development of..."
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* Education */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-700">Education</h3>
                <button
                  onClick={addEducation}
                  className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                >
                  + Add Education
                </button>
              </div>
              {resumeData.education.map((edu, index) => (
                <div key={index} className="p-4 bg-gray-50 rounded border border-gray-200 space-y-2">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-500">Education #{index + 1}</span>
                    {resumeData.education.length > 1 && (
                      <button
                        onClick={() => removeEducation(index)}
                        className="text-red-600 text-sm hover:text-red-800"
                      >
                        Remove
                      </button>
                    )}
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Degree</label>
                    <input
                      type="text"
                      value={edu.degree}
                      onChange={(e) => updateEducation(index, 'degree', e.target.value)}
                      className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Bachelor of Science in Computer Science"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">Institution</label>
                      <input
                        type="text"
                        value={edu.institution}
                        onChange={(e) => updateEducation(index, 'institution', e.target.value)}
                        className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Stanford University"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">Location</label>
                      <input
                        type="text"
                        value={edu.location}
                        onChange={(e) => updateEducation(index, 'location', e.target.value)}
                        className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Stanford, CA"
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">Graduation Date</label>
                      <input
                        type="text"
                        value={edu.graduationDate}
                        onChange={(e) => updateEducation(index, 'graduationDate', e.target.value)}
                        className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="May 2018"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">GPA</label>
                      <input
                        type="text"
                        value={edu.gpa}
                        onChange={(e) => updateEducation(index, 'gpa', e.target.value)}
                        className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="3.8"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Skills */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-gray-700">Skills</h3>
              <textarea
                value={resumeData.skills}
                onChange={(e) => updateData({ ...resumeData, skills: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[80px]"
                placeholder="JavaScript, React, Node.js, Python, Docker, Kubernetes..."
              />
              <p className="text-xs text-gray-500">Enter skills separated by commas</p>

              {/* Keyword Suggestions */}
              {currentScore && (keywordSuggestions.missing.length > 0 || keywordSuggestions.present.length > 0) && (
                <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded">
                  <div className="text-xs font-semibold text-blue-800 mb-2">Keyword Suggestions:</div>
                  {keywordSuggestions.missing.length > 0 && (
                    <div className="mb-2">
                      <span className="text-xs text-red-600 font-medium">Missing: </span>
                      <span className="text-xs text-gray-700">{keywordSuggestions.missing.join(', ')}</span>
                    </div>
                  )}
                  {keywordSuggestions.present.length > 0 && (
                    <div>
                      <span className="text-xs text-green-600 font-medium">✓ Present: </span>
                      <span className="text-xs text-gray-700">{keywordSuggestions.present.join(', ')}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* RIGHT 50% - Live Preview */}
        <div className="w-1/2 overflow-y-auto bg-white p-8">
          <style>{`
            .resume-preview {
              max-width: 850px;
              margin: 0 auto;
              font-family: 'Calibri', 'Arial', sans-serif;
              font-size: 11pt;
              line-height: 1.4;
              color: #000;
            }
            .resume-preview h1 {
              font-size: 24pt;
              font-weight: bold;
              color: #008080;
              margin: 0 0 8px 0;
              letter-spacing: 0.5px;
            }
            .resume-preview h2 {
              font-size: 13pt;
              font-weight: bold;
              color: #1f4788;
              margin: 16px 0 8px 0;
              text-transform: uppercase;
              border-bottom: 2px solid #1f4788;
              padding-bottom: 2px;
              letter-spacing: 0.5px;
            }
            .resume-preview h3 {
              font-size: 11pt;
              font-weight: bold;
              margin: 8px 0 4px 0;
              color: #000;
            }
            .resume-preview p {
              margin: 4px 0;
              line-height: 1.4;
            }
            .resume-preview strong {
              font-weight: bold;
            }
            .resume-preview em {
              font-style: italic;
            }
            .resume-preview ul, .resume-preview ol {
              margin: 4px 0;
              padding-left: 25px;
            }
            .resume-preview li {
              margin: 3px 0;
              line-height: 1.4;
            }
          `}</style>
          <div
            className="resume-preview"
            dangerouslySetInnerHTML={{ __html: convertToHTML(resumeData) }}
          />
        </div>
      </div>
    </div>
  );
};
