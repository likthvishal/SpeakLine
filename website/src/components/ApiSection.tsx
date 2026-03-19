import { useState } from 'react';

type TabType = 'basic' | 'custom' | 'jupyter';

export default function ApiSection() {
  const [activeTab, setActiveTab] = useState<TabType>('basic');

  const tabs: { id: TabType; label: string }[] = [
    { id: 'basic', label: 'Basic Usage' },
    { id: 'custom', label: 'Custom Transcriber' },
    { id: 'jupyter', label: 'Jupyter Notebook' },
  ];

  const codeExamples = {
    basic: `from speakline import VoiceCommenter

# Auto-detect language from file extension
commenter = VoiceCommenter()
commenter.record_and_insert('myfile.py', line_number=42)

# Or specify language explicitly
commenter = VoiceCommenter(language='python')
commenter.record_and_insert('main.py', line_number=15)

# Transcribe only (no file modification)
text = commenter.transcribe_only()
print(text)  # "This function calculates factorial"

# Insert into code string (no file I/O)
code = """
def factorial(n):
    return n * factorial(n - 1) if n > 1 else 1
"""
updated = commenter.insert_comment_to_string(
    code,
    "Base case for recursion",
    line_number=3
)`,
    custom: `from speakline import VoiceCommenter
from speakline.transcriber import TranscriberBase
import numpy as np

class CustomLLMTranscriber(TranscriberBase):
    """Use your own LLM for transcription."""

    def transcribe(
        self,
        audio: np.ndarray,
        sample_rate: int = 16000
    ) -> str:
        # Your custom LLM logic here
        # Could use GPT-4, Claude, local model, etc.
        return "custom transcription"

# Use your custom transcriber
commenter = VoiceCommenter(
    transcriber=CustomLLMTranscriber()
)
commenter.record_and_insert('file.py', line_number=10)`,
    jupyter: `from speakline import VoiceCommenter

commenter = VoiceCommenter(language='python')

# Your cell code
code_str = """
def process_data(df):
    return df.dropna()
"""

# Record voice and get transcription
comment = commenter.transcribe_only(duration=5)

# Insert into your code
updated = commenter.insert_comment_to_string(
    code_str,
    comment,
    line_number=2
)

print(updated)
# Output:
# def process_data(df):
#     # Remove rows with missing values
#     return df.dropna()`,
  };

  return (
    <section id="api" className="py-24 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Powerful
            <span className="gradient-text"> Python API</span>
          </h2>
          <p className="text-gray-500 text-lg max-w-2xl mx-auto">
            Full programmatic access. Build integrations, extend functionality, or create custom workflows.
          </p>
        </div>

        {/* Code Examples */}
        <div className="max-w-4xl mx-auto">
          <div className="glass rounded-2xl overflow-hidden">
            {/* Tabs */}
            <div className="flex border-b border-gray-200 overflow-x-auto">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-6 py-3 text-sm font-medium whitespace-nowrap transition-colors ${
                    activeTab === tab.id
                      ? 'text-gray-900 bg-gray-50 border-b-2 border-gray-900'
                      : 'text-gray-500 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Code Content */}
            <div className="p-0">
              <div className="code-block rounded-none border-0">
                <pre className="p-6 text-sm overflow-x-auto max-h-[500px]">
                  <code>
                    {codeExamples[activeTab].split('\n').map((line, i) => (
                      <div key={i} className="flex">
                        <span className="text-gray-400 w-8 text-right mr-4 select-none text-xs">
                          {i + 1}
                        </span>
                        <span>
                          {line.startsWith('#') || line.trim().startsWith('#') ? (
                            <span className="token-comment">{line}</span>
                          ) : line.includes('"""') ? (
                            <span className="token-string">{line}</span>
                          ) : line.includes('from ') || line.includes('import ') ? (
                            <>
                              <span className="token-keyword">
                                {line.split(' ')[0]}
                              </span>
                              <span className="text-gray-700">
                                {' ' + line.split(' ').slice(1).join(' ')}
                              </span>
                            </>
                          ) : line.includes('class ') ? (
                            <>
                              <span className="token-keyword">class</span>
                              <span className="text-gray-700">{line.slice(5)}</span>
                            </>
                          ) : line.includes('def ') ? (
                            <>
                              <span className="text-gray-700">{line.split('def')[0]}</span>
                              <span className="token-keyword">def</span>
                              <span className="token-function">{line.split('def')[1].split('(')[0]}</span>
                              <span className="text-gray-700">({line.split('(').slice(1).join('(')}</span>
                            </>
                          ) : line.includes('return ') ? (
                            <>
                              <span className="text-gray-700">{line.split('return')[0]}</span>
                              <span className="token-keyword">return</span>
                              <span className="text-gray-700">{line.split('return')[1]}</span>
                            </>
                          ) : line.includes('print(') ? (
                            <>
                              <span className="token-function">print</span>
                              <span className="text-gray-700">{line.slice(5)}</span>
                            </>
                          ) : (
                            <span className="text-gray-700">{line}</span>
                          )}
                        </span>
                      </div>
                    ))}
                  </code>
                </pre>
              </div>
            </div>
          </div>

          {/* API Highlights */}
          <div className="grid sm:grid-cols-3 gap-4 mt-8">
            {[
              { label: 'Type Hints', desc: 'Full typing support for IDE autocomplete' },
              { label: 'Error Handling', desc: 'Comprehensive exceptions with clear messages' },
              { label: 'Extensible', desc: 'Abstract base classes for custom backends' },
            ].map((item, i) => (
              <div key={i} className="text-center p-4 glass rounded-xl">
                <h4 className="text-gray-900 font-medium mb-1">{item.label}</h4>
                <p className="text-gray-400 text-sm">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
