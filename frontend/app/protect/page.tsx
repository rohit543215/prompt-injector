'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'
import { Shield, AlertTriangle, CheckCircle, Copy, RefreshCw, Lightbulb, ArrowLeft } from 'lucide-react'
import Link from 'next/link'

const API_BASE = 'http://localhost:8000'

interface PromptProtectionResult {
  original_prompt: string
  protected_prompt: string
  protection_applied: boolean
  detected_pii: any[]
  replacements_made: any[]
  suggestions: string[]
  context: string
  risk_level: string
  pii_count: number
  pii_types: string[]
  alternatives?: string[]
}

interface PromptExample {
  category: string
  original: string
  protected: string
  risk_level: string
}

export default function PromptProtector() {
  const [inputPrompt, setInputPrompt] = useState('')
  const [protectionResult, setProtectionResult] = useState<PromptProtectionResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [examples, setExamples] = useState<PromptExample[]>([])
  const [showAlternatives, setShowAlternatives] = useState(false)

  useEffect(() => {
    loadExamples()
  }, [])

  const loadExamples = async () => {
    try {
      const response = await axios.get(`${API_BASE}/prompt-examples`)
      setExamples(response.data.examples)
    } catch (err) {
      console.error('Failed to load examples:', err)
    }
  }

  const protectPrompt = async () => {
    if (!inputPrompt.trim()) {
      setError('Please enter a prompt to protect')
      return
    }

    setLoading(true)
    setError('')
    
    try {
      const response = await axios.post(`${API_BASE}/protect-prompt`, {
        prompt: inputPrompt,
        num_alternatives: showAlternatives ? 3 : 0
      })
      setProtectionResult(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Protection failed')
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const loadExample = (example: PromptExample) => {
    setInputPrompt(example.original)
    setProtectionResult(null)
    setError('')
  }

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'HIGH': return 'text-red-600 bg-red-100'
      case 'MEDIUM': return 'text-yellow-600 bg-yellow-100'
      case 'LOW': return 'text-green-600 bg-green-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getRiskIcon = (riskLevel: string) => {
    switch (riskLevel) {
      case 'HIGH': return <AlertTriangle className="w-4 h-4" />
      case 'MEDIUM': return <AlertTriangle className="w-4 h-4" />
      case 'LOW': return <CheckCircle className="w-4 h-4" />
      default: return <Shield className="w-4 h-4" />
    }
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Header */}
      <div className="mb-8">
        <Link href="/" className="inline-flex items-center text-blue-600 hover:text-blue-800 mb-4">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to PII Detection
        </Link>
        
        <div className="flex items-center mb-4">
          <Shield className="w-10 h-10 text-green-600 mr-3" />
          <h1 className="text-3xl font-bold text-gray-800">Prompt Protector</h1>
        </div>
        <p className="text-lg text-gray-600">
          Generate privacy-safe versions of your prompts while maintaining their intent and effectiveness
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Input Section */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-4 flex items-center">
              <Shield className="w-6 h-6 mr-2 text-green-600" />
              Protect Your Prompt
            </h2>
            
            {/* Examples */}
            {examples.length > 0 && (
              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-2">Try these example prompts:</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {examples.map((example, index) => (
                    <button
                      key={index}
                      onClick={() => loadExample(example)}
                      className="p-3 text-left bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                      <div className="font-medium text-sm text-gray-800">{example.category}</div>
                      <div className="text-xs text-gray-600 mt-1 truncate">{example.original}</div>
                      <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs mt-2 ${getRiskColor(example.risk_level)}`}>
                        {getRiskIcon(example.risk_level)}
                        <span className="ml-1">{example.risk_level} Risk</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            <textarea
              value={inputPrompt}
              onChange={(e) => setInputPrompt(e.target.value)}
              placeholder="Enter your prompt here... (e.g., 'Write an email to John Smith at john@company.com about the project update')"
              className="w-full h-32 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
            />
            
            <div className="flex items-center justify-between mt-4">
              <div className="flex items-center space-x-4">
                <div className="text-sm text-gray-500">
                  {inputPrompt.length} characters
                </div>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={showAlternatives}
                    onChange={(e) => setShowAlternatives(e.target.checked)}
                    className="mr-2"
                  />
                  <span className="text-sm text-gray-600">Generate alternatives</span>
                </label>
              </div>
              <button
                onClick={protectPrompt}
                disabled={loading || !inputPrompt.trim()}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Protecting...
                  </>
                ) : (
                  <>
                    <Shield className="w-4 h-4 mr-2" />
                    Protect Prompt
                  </>
                )}
              </button>
            </div>

            {error && (
              <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
                {error}
              </div>
            )}
          </div>

          {/* Results Section */}
          {protectionResult && (
            <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold">Protection Results</h3>
                <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm ${getRiskColor(protectionResult.risk_level)}`}>
                  {getRiskIcon(protectionResult.risk_level)}
                  <span className="ml-1">{protectionResult.risk_level} Risk</span>
                </div>
              </div>

              <div className="space-y-6">
                {/* Original vs Protected */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-red-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-red-800">Original Prompt</span>
                      <button
                        onClick={() => copyToClipboard(protectionResult.original_prompt)}
                        className="p-1 text-red-600 hover:text-red-800"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                    </div>
                    <div className="text-sm text-red-700 leading-relaxed">
                      {protectionResult.original_prompt}
                    </div>
                  </div>

                  <div className="p-4 bg-green-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-green-800">Protected Prompt</span>
                      <button
                        onClick={() => copyToClipboard(protectionResult.protected_prompt)}
                        className="p-1 text-green-600 hover:text-green-800"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                    </div>
                    <div className="text-sm text-green-700 leading-relaxed">
                      {protectionResult.protected_prompt}
                    </div>
                  </div>
                </div>

                {/* Alternatives */}
                {protectionResult.alternatives && protectionResult.alternatives.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-3 flex items-center">
                      <RefreshCw className="w-4 h-4 mr-2" />
                      Alternative Protected Versions
                    </h4>
                    <div className="space-y-2">
                      {protectionResult.alternatives.map((alt, index) => (
                        <div key={index} className="p-3 bg-blue-50 rounded-lg">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm font-medium text-blue-800">Alternative {index + 1}</span>
                            <button
                              onClick={() => copyToClipboard(alt)}
                              className="p-1 text-blue-600 hover:text-blue-800"
                            >
                              <Copy className="w-4 h-4" />
                            </button>
                          </div>
                          <div className="text-sm text-blue-700">{alt}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Replacements Made */}
                {protectionResult.replacements_made && protectionResult.replacements_made.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-3">Replacements Made</h4>
                    <div className="space-y-2">
                      {protectionResult.replacements_made.map((replacement, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div className="flex items-center space-x-3">
                            <span className="text-sm text-red-600 font-mono bg-red-100 px-2 py-1 rounded">
                              {replacement.original}
                            </span>
                            <span className="text-gray-400">→</span>
                            <span className="text-sm text-green-600 font-mono bg-green-100 px-2 py-1 rounded">
                              {replacement.replacement}
                            </span>
                          </div>
                          <span className="text-xs text-gray-500 bg-gray-200 px-2 py-1 rounded">
                            {replacement.type.replace('_', ' ')}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Statistics */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="p-3 bg-blue-50 rounded-lg text-center">
                    <div className="text-2xl font-bold text-blue-600">{protectionResult.pii_count}</div>
                    <div className="text-sm text-blue-800">PII Items Found</div>
                  </div>
                  <div className="p-3 bg-purple-50 rounded-lg text-center">
                    <div className="text-2xl font-bold text-purple-600">{protectionResult.pii_types.length}</div>
                    <div className="text-sm text-purple-800">PII Types</div>
                  </div>
                  <div className="p-3 bg-orange-50 rounded-lg text-center">
                    <div className="text-lg font-bold text-orange-600 capitalize">{protectionResult.context}</div>
                    <div className="text-sm text-orange-800">Context</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Suggestions */}
          {protectionResult && protectionResult.suggestions.length > 0 && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Lightbulb className="w-5 h-5 mr-2 text-yellow-600" />
                Privacy Tips
              </h3>
              <div className="space-y-3">
                {protectionResult.suggestions.map((suggestion, index) => (
                  <div key={index} className="p-3 bg-yellow-50 rounded-lg">
                    <div className="text-sm text-yellow-800">{suggestion}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* How it Works */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold mb-4">How Prompt Protection Works</h3>
            <div className="space-y-3 text-sm text-gray-600">
              <div className="flex items-start">
                <div className="w-6 h-6 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-xs font-bold mr-3 mt-0.5">1</div>
                <div>Scans your prompt for personally identifiable information</div>
              </div>
              <div className="flex items-start">
                <div className="w-6 h-6 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-xs font-bold mr-3 mt-0.5">2</div>
                <div>Replaces PII with realistic but generic alternatives</div>
              </div>
              <div className="flex items-start">
                <div className="w-6 h-6 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-xs font-bold mr-3 mt-0.5">3</div>
                <div>Maintains the original intent and context of your prompt</div>
              </div>
              <div className="flex items-start">
                <div className="w-6 h-6 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-xs font-bold mr-3 mt-0.5">4</div>
                <div>Provides suggestions for better privacy practices</div>
              </div>
            </div>
          </div>

          {/* Risk Levels */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Risk Levels</h3>
            <div className="space-y-3">
              <div className="flex items-center">
                <div className="w-4 h-4 bg-red-500 rounded-full mr-3"></div>
                <div>
                  <div className="font-medium text-sm">HIGH</div>
                  <div className="text-xs text-gray-600">SSN, credit cards, bank accounts</div>
                </div>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 bg-yellow-500 rounded-full mr-3"></div>
                <div>
                  <div className="font-medium text-sm">MEDIUM</div>
                  <div className="text-xs text-gray-600">Emails, phones, addresses</div>
                </div>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 bg-green-500 rounded-full mr-3"></div>
                <div>
                  <div className="font-medium text-sm">LOW</div>
                  <div className="text-xs text-gray-600">Names, organizations, locations</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}