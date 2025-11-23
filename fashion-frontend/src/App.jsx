// src/App.jsx — FINAL, BULLETPROOF, NO MORE 406 EVER (2025-11-22)
import React, { useState, useRef } from 'react';
import './App.css';

export default function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [error, setError] = useState('');
  const carouselRef = useRef(null);

  const handleSubmit = async () => {
    if (!file) return;

    setLoading(true);
    setError('');
    setRecommendations([]);

    try {
      // 1. Convert image to base64
      const base64 = await new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result.split(',')[1]);
        reader.readAsDataURL(file);
      });

      // 2. Initialize — FIXED: ADD text/event-stream TO ACCEPT
      const initResp = await fetch('http://localhost:8000/mcp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json,text/event-stream',  // ← THIS IS THE FIX: BOTH TYPES FOR ALL REQUESTS
        },
        body: JSON.stringify({
          jsonrpc: '2.0',
          id: 1,
          method: 'initialize',
          params: {
            protocolVersion: '2025-03-26',  // ← CORRECT VERSION FROM MCP SPEC
            capabilities: {},                // ← REQUIRED
            clientInfo: { 
              name: 'fashion-web', 
              version: '1.0.0' 
            },
          },
        }),
      });

      if (!initResp.ok) {
        const text = await initResp.text();
        throw new Error(`Initialize failed: ${initResp.status}\n${text}`);
      }

      const sessionId = initResp.headers.get('mcp-session-id');
      if (!sessionId) throw new Error('No mcp-session-id header');

      console.log('Session initialized:', sessionId);

      // 3. Call tool — SAME HEADERS AS INIT
      const toolResp = await fetch('http://localhost:8000/mcp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json,text/event-stream',  // ← BOTH TYPES
          'mcp-session-id': sessionId,
        },
        body: JSON.stringify({
          jsonrpc: '2.0',
          id: Date.now(),
          method: 'tools/call',
          params: {
            name: 'fashion_recommendation_tool',
            arguments: {
              args:{

                image_bytes: base64,
              }
            },
          },
        }),
      });

      if (!toolResp.ok) {
        const text = await toolResp.text();
        throw new Error(`Tool call failed: ${toolResp.status}\n${text}`);
      }

      // Handle possible streaming response
      const contentType = toolResp.headers.get('content-type');
      if (contentType && contentType.includes('text/event-stream')) {
        // Stream parsing for SSE
        const reader = toolResp.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6).trim();
              if (!data || data === '[DONE]') continue;

              try {
                const parsed = JSON.parse(data);
                console.log('Stream chunk:', parsed);

                if (parsed.result?.content?.[0]?.text) {
                  const text = parsed.result.content[0].text;
                  const jsonResult = JSON.parse(text);
                  if (jsonResult.recommendations) {
                    setRecommendations(jsonResult.recommendations);
                  }
                }
              } catch (err) {
                console.warn('Parse error:', err);
              }
            }
          }
        }
      } else {
        // Regular JSON
        const data = await toolResp.json();
        console.log('TOOL RESPONSE:', data);

        let recs = [];
        if (data.result?.content?.[0]?.text) {
          const text = data.result.content[0].text;
          const parsed = JSON.parse(text);
          recs = parsed.recommendations || [];
        } else if (data.result?.recommendations) {
          recs = data.result.recommendations;
        }

        console.log('RECOMMENDATIONS:', recs);
        setRecommendations(recs);
      }

    } catch (err) {
      console.error('ERROR:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const scroll = (dir) => {
    if (carouselRef.current) {
      carouselRef.current.scrollBy({
        left: dir === 'left' ? -420 : 420,
        behavior: 'smooth',
      });
    }
  };

  return (
    <div className="background-container">
      <div className="max-w-7xl mx-auto text-white py-20 px-8 text-center">
        <h1 className="text-8xl font-black mb-6 tracking-tighter">AI FASHION</h1>
        <p className="text-3xl mb-16 opacity-90">Upload any outfit → Get real matches instantly</p>

        {/* Upload */}
        <div className="mb-16">
          <label className="button-one text-4xl px-16 py-10 cursor-pointer inline-block">
            Choose Photo
            <input
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) {
                  setFile(f);
                  setPreview(URL.createObjectURL(f));
                  setRecommendations([]);
                  setError('');
                }
              }}
            />
          </label>
        </div>

        {/* Preview */}
        {preview && (
          <div className="flex justify-center my-20">
            <img
              src={preview}
              alt="Your outfit"
              className="max-w-2xl rounded-3xl shadow-2xl border-8 border-white/20"
            />
          </div>
        )}

        {/* Submit */}
        <button
          onClick={handleSubmit}
          disabled={!file || loading}
          className="button-two text-5xl px-28 py-14 disabled:opacity-50 mb-20"
        >
          {loading ? 'Analyzing Outfit...' : 'Get Recommendations'}
        </button>

        {/* CAROUSEL */}
        {recommendations.length > 0 && (
          <div className="relative">
            <h2 className="text-7xl font-black mb-16">YOUR PERFECT MATCHES</h2>

            <button 
              onClick={() => scroll('left')} 
              className="carousel-arrow left-arrow text-8xl absolute left-0 top-1/2 -translate-y-1/2"
            >
              ‹
            </button>
            <button 
              onClick={() => scroll('right')} 
              className="carousel-arrow right-arrow text-8xl absolute right-0 top-1/2 -translate-y-1/2"
            >
              ›
            </button>

            <div className="carousel-container" ref={carouselRef}>
              {recommendations.map((item, i) => (
                <div key={item.sku || i} className="carousel-item">
                  <div className="image-wrapper">
                    <img
                      src={item.url}
                      alt={item.title || 'Product'}
                      className="rounded-3xl shadow-2xl object-cover"
                      loading="lazy"
                    />
                  </div>
                  <h3 className="text-3xl font-bold mt-8">{item.title || 'Untitled'}</h3>
                  <p className="text-5xl font-black text-yellow-400 mt-4">
                    ${item.price?.toFixed(2) || '??'}
                  </p>
                  <p className="text-lg opacity-80 mt-2">Score: {item.score?.toFixed(3)}</p>
                  {item.reason && (
                    <p className="text-sm italic mt-3 opacity-60">{item.reason}</p>
                  )}
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="view-link text-2xl mt-6 inline-block"
                  >
                    View Product →
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mt-20 p-12 bg-red-900/70 rounded-3xl text-2xl max-w-4xl mx-auto">
            <p>{error}</p>
          </div>
        )}
      </div>
    </div>
  );
}