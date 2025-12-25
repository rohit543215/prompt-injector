'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'
import { Shield, Eye, EyeOff, Brain, Zap, Lock, Unlock, ArrowRight } from 'lucide-react'
import Link from 'next/link'

const API_BASE = 'http://localhost:8000'

interface PIIEntity {
  text: string
  type: string
  confidence: number
}

interface AnalysisResult {
  original_text: string
  masked_text: string
  detected_entities: PIIEntity[]
  pii_count: number
  pii_types: string[]
  mask_info: any[]
}

interface SampleText {
  title: string
  text: string
}

export default function Home() {
  const [inputText, setInputText] = useState('')
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showMasked, setShowMasked] = useState(false)
  const [apiHealth, setApiHealth] = useState<any>(null)
  const [sampleTexts, setSampleTexts] = useState<SampleText[]>([])

  useEffect(() => {
    checkApiHealth()
    loadSampleTexts()
  }, [])

  const checkApiHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE}/health`)
      setApiHealth(response.data)
    } catch (err) {
      console.error('API health check failed:', err)
    }
  }

  const loadSampleTexts = async () => {
    try {
      const response = await axios.get(`${API_BASE}/demo/sample-texts`)
      setSampleTexts(response.data.samples)
    } catch (err) {
      console.error('Failed to load sample texts:', err)
    }
  }

  const analyzeText = async () => {
    if (!inputText.trim()) {
      setError('Please enter some text to analyze')
      return
    }

    setLoading(true)
    setError('')
    
    try {
      const response = await axios.post(`${API_BASE}/analyze`, {
        text: inputText
      })
      setAnalysisResult(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const loadSampleText = (sample: SampleText) => {
    setInputText(sample.text)
    setAnalysisResult(null)
    setError('')
  }

  const highlightPII = (text: string, entities: PIIEntity[]) => {
    if (!entities.length) return text

    let highlightedText = text
    const sortedEntities = [...entities].sort((a, b) => b.text.length - a.text.length)

    sortedEntities.forEach((entity, index) => {
      const regex = new RegExp(`\\b${entity.text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'g')
      highlightedText = highlightedText.replace(
        regex,
        `<span class="pii-highlight pii-${entity.type}" title="${entity.type} (${(entity.confidence * 100).toFixed(1)}% confidence)">${entity.text}</span>`
      )
    })

    return highlightedText
  }

  const getPIITypeColor = (type: string) => {
    const colors: { [key: string]: string } = {
      'PERSON': 'bg-blue-100 text-blue-800',
      'EMAIL': 'bg-green-100 text-green-800',
      'PHONE': 'bg-purple-100 text-purple-800',
      'SSN': 'bg-red-100 text-red-800',
      'CREDIT_CARD': 'bg-orange-100 text-orange-800',
      'ADDRESS': 'bg-indigo-100 text-indigo-800',
      'DATE': 'bg-pink-100 text-pink-800',
      'ORGANIZATION': 'bg-teal-100 text-teal-800',
      'LOCATION': 'bg-cyan-100 text-cyan-800',
      'IP_ADDRESS': 'bg-gray-100 text-gray-800',
      'URL': 'bg-lime-100 text-lime-800',
      'BANK_ACCOUNT': 'bg-amber-100 text-amber-800'
    }
    return colors[type] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center mb-4">
          <Shield className="w-12 h-12 text-blue-600 mr-3" />
          <h1 className="text-4xl font-bold text-gray-800">PII Detection & Masking</h1>
        </div>
        <p className="text-lg text-gray-600 mb-4">
          Neural Network-powered Personally Identifiable Information detection and masking system
        </p>
        
        {/* Navigation */}
        <div className="flex items-center justify-center space-x-4 mb-4">
          <Link 
            href="/protect" 
            className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Shield className="w-4 h-4 mr-2" />
            Prompt Protector
            <ArrowRight className="w-4 h-4 ml-2" />
          </Link>
        </div>
        
        {/* API Status */}
        <div className="flex items-center justify-center space-x-4 text-sm">
          <div className={`flex items-center px-3 py-1 rounded-full ${
            apiHealth?.status === 'healthy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            <div className={`w-2 h-2 rounded-full mr-2 ${
              apiHealth?.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
            }`}></div>
            API {apiHealth?.status || 'Unknown'}
          </div>
          <div className={`flex items-center px-3 py-1 rounded-full ${
            apiHealth?.model_loaded ? 'bg-blue-100 text-blue-800' : 'bg-yellow-100 text-yellow-800'
          }`}>
            <Brain className="w-3 h-3 mr-1" />
            Model {apiHealth?.model_loaded ? 'Loaded' : 'Not Loaded'}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Input Section */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-4 flex items-center">
              <Zap className="w-6 h-6 mr-2 text-blue-600" />
              Text Analysis
            </h2>
            
            {/* Sample Texts */}
            {sampleTexts.length > 0 && (
              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-2">Try these sample texts:</p>
                <div className="flex flex-wrap gap-2">
                  {sampleTexts.map((sample, index) => (
                    <button
                      key={index}
                      onClick={() => loadSampleText(sample)}
                      className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors"
                    >
                      {sample.title}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Enter text to analyze for PII (names, emails, phone numbers, etc.)..."
              className="w-full h-40 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
            
            <div className="flex items-center justify-between mt-4">
              <div className="text-sm text-gray-500">
                {inputText.length} characters
              </div>
              <button
                onClick={analyzeText}
                disabled={loading || !inputText.trim()}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Brain className="w-4 h-4 mr-2" />
                    Analyze PII
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
          {analysisResult && (
            <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold">Analysis Results</h3>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setShowMasked(!showMasked)}
                    className="flex items-center px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                  >
                    {showMasked ? (
                      <>
                        <EyeOff className="w-4 h-4 mr-1" />
                        Show Original
                      </>
                    ) : (
                      <>
                        <Eye className="w-4 h-4 mr-1" />
                        Show Masked
                      </>
                    )}
                  </button>
                </div>
              </div>

              <div className="space-y-4">
                {/* Text Display */}
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center mb-2">
                    {showMasked ? (
                      <Lock className="w-4 h-4 mr-2 text-red-600" />
                    ) : (
                      <Unlock className="w-4 h-4 mr-2 text-green-600" />
                    )}
                    <span className="font-medium">
                      {showMasked ? 'Masked Text (Safe for AI)' : 'Original Text with PII Highlighted'}
                    </span>
                  </div>
                  <div 
                    className="text-sm leading-relaxed"
                    dangerouslySetInnerHTML={{
                      __html: showMasked 
                        ? analysisResult.masked_text.replace(/\n/g, '<br>')
                        : highlightPII(analysisResult.original_text, analysisResult.detected_entities).replace(/\n/g, '<br>')
                    }}
                  />
                </div>

                {/* Statistics */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">{analysisResult.pii_count}</div>
                    <div className="text-sm text-blue-800">PII Entities Found</div>
                  </div>
                  <div className="p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">{analysisResult.pii_types.length}</div>
                    <div className="text-sm text-green-800">Different PII Types</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* PII Types Legend */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Supported PII Types</h3>
            <div className="space-y-2">
              {[
                'PERSON', 'EMAIL', 'PHONE', 'SSN', 'CREDIT_CARD',
                'ADDRESS', 'DATE', 'ORGANIZATION', 'LOCATION',
                'IP_ADDRESS', 'URL', 'BANK_ACCOUNT'
              ].map((type) => (
                <div key={type} className="flex items-center">
                  <span className={`px-2 py-1 rounded text-xs font-medium mr-2 ${getPIITypeColor(type)}`}>
                    {type.replace('_', ' ')}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Detected Entities */}
          {analysisResult && analysisResult.detected_entities.length > 0 && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Detected Entities</h3>
              <div className="space-y-3">
                {analysisResult.detected_entities.map((entity, index) => (
                  <div key={index} className="border-l-4 border-blue-500 pl-3">
                    <div className="font-medium text-sm">{entity.text}</div>
                    <div className="flex items-center justify-between text-xs text-gray-600">
                      <span className={`px-2 py-1 rounded ${getPIITypeColor(entity.type)}`}>
                        {entity.type.replace('_', ' ')}
                      </span>
                      <span>{(entity.confidence * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* How it Works */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold mb-4">How It Works</h3>
            <div className="space-y-3 text-sm text-gray-600">
              <div className="flex items-start">
                <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-bold mr-3 mt-0.5">1</div>
                <div>Neural network analyzes text using transformer-based NER model</div>
              </div>
              <div className="flex items-start">
                <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-bold mr-3 mt-0.5">2</div>
                <div>Identifies 12 types of PII with confidence scores</div>
              </div>
              <div className="flex items-start">
                <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-bold mr-3 mt-0.5">3</div>
                <div>Masks sensitive data before sending to AI systems</div>
              </div>
              <div className="flex items-start">
                <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-bold mr-3 mt-0.5">4</div>
                <div>Restores original PII in responses when appropriate</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}