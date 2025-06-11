// Phase 2: Conflict Detection Frontend Module
class ConflictDetector {
    constructor() {
        this.conflictData = null;
        this.isLoading = false;
        console.log('ConflictDetector initialized');
    }

    async detectConflicts() {
        console.log('Starting conflict detection...');
        this.isLoading = true;
        this.updateLoadingState();

        try {
            console.log('Fetching from /.netlify/functions/detect-conflicts');
            const response = await fetch('/.netlify/functions/detect-conflicts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            });

            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            this.conflictData = await response.json();
            console.log('Conflict data received:', this.conflictData);
            this.displayResults();
        } catch (error) {
            console.error('Error detecting conflicts:', error);
            this.displayError(error.message);
        } finally {
            this.isLoading = false;
            this.updateLoadingState();
        }
    }

    updateLoadingState() {
        const loadingElement = document.getElementById('conflict-loading');
        const resultsElement = document.getElementById('conflict-results');
        
        console.log('Updating loading state:', { loading: this.isLoading, loadingElement: !!loadingElement, resultsElement: !!resultsElement });
        
        if (loadingElement) {
            loadingElement.style.display = this.isLoading ? 'block' : 'none';
        }
        if (resultsElement) {
            resultsElement.style.display = this.isLoading ? 'none' : 'block';
        }
    }

    displayResults() {
        console.log('Displaying results...');
        if (!this.conflictData) {
            console.log('No conflict data to display');
            return;
        }

        const resultsContainer = document.getElementById('conflict-results');
        if (!resultsContainer) {
            console.error('Results container not found');
            return;
        }

        const { summary, conflicts, deprecated_articles, relevance_scores, recommendations } = this.conflictData;
        console.log('Summary:', summary);

        resultsContainer.innerHTML = `
            <div class="conflict-summary">
                <h3>📊 Knowledge Base Health Report</h3>
                <div class="health-metrics">
                    <div class="metric-card ${recommendations.total_kb_health_score >= 80 ? 'good' : recommendations.total_kb_health_score >= 60 ? 'warning' : 'critical'}">
                        <div class="metric-value">${recommendations.total_kb_health_score}%</div>
                        <div class="metric-label">Overall Health Score</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${summary.total_articles}</div>
                        <div class="metric-label">Total Articles</div>
                    </div>
                    <div class="metric-card ${summary.conflicts_found > 0 ? 'warning' : 'good'}">
                        <div class="metric-value">${summary.conflicts_found}</div>
                        <div class="metric-label">Conflicts Found</div>
                    </div>
                    <div class="metric-card ${summary.deprecated_articles > 0 ? 'critical' : 'good'}">
                        <div class="metric-value">${summary.deprecated_articles}</div>
                        <div class="metric-label">Deprecated Articles</div>
                    </div>
                </div>
            </div>

            <div class="action-summary">
                <h4>🎯 Action Required</h4>
                <div class="action-items">
                    <div class="action-item critical">
                        <strong>${recommendations.immediate_action}</strong> items need immediate attention
                    </div>
                    <div class="action-item warning">
                        <strong>${recommendations.review_needed}</strong> items need review
                    </div>
                </div>
            </div>

            ${this.renderConflicts(conflicts)}
            ${this.renderDeprecatedArticles(deprecated_articles)}
            ${this.renderRelevanceScores(relevance_scores)}
        `;
        
        console.log('Results displayed successfully');
    }

    renderConflicts(conflicts) {
        console.log('Rendering conflicts:', conflicts?.length || 0);
        if (!conflicts || conflicts.length === 0) {
            return `
                <div class="section-container">
                    <h4>✅ Article Conflicts</h4>
                    <div class="no-conflicts">No conflicts detected between articles!</div>
                </div>
            `;
        }

        const conflictHtml = conflicts.map(conflict => `
            <div class="conflict-item ${conflict.severity.toLowerCase()}">
                <div class="conflict-header">
                    <span class="severity-badge ${conflict.severity.toLowerCase()}">${conflict.severity}</span>
                    <span class="conflict-category">${conflict.conflict_category.replace('_', ' ').toUpperCase()}</span>
                    <span class="conflict-score">Score: ${(conflict.conflict_score * 100).toFixed(0)}%</span>
                </div>
                <div class="conflict-articles">
                    <div class="article-info">
                        <strong>${conflict.article1.title}</strong>
                        <div class="article-meta">
                            Author: ${conflict.article1.author || 'Unknown'} | 
                            Version: ${conflict.article1.version || 'N/A'}
                        </div>
                    </div>
                    <div class="vs-indicator">⚡ CONFLICTS WITH ⚡</div>
                    <div class="article-info">
                        <strong>${conflict.article2.title}</strong>
                        <div class="article-meta">
                            Author: ${conflict.article2.author || 'Unknown'} | 
                            Version: ${conflict.article2.version || 'N/A'}
                        </div>
                    </div>
                </div>
                <div class="conflict-recommendation">
                    <strong>Recommendation:</strong> ${conflict.recommendation}
                </div>
            </div>
        `).join('');

        return `
            <div class="section-container">
                <h4>⚡ Article Conflicts (${conflicts.length})</h4>
                <div class="conflicts-list">
                    ${conflictHtml}
                </div>
            </div>
        `;
    }

    renderDeprecatedArticles(deprecatedArticles) {
        console.log('Rendering deprecated articles:', deprecatedArticles?.length || 0);
        if (!deprecatedArticles || deprecatedArticles.length === 0) {
            return `
                <div class="section-container">
                    <h4>✅ Deprecated Content</h4>
                    <div class="no-deprecated">No deprecated content detected!</div>
                </div>
            `;
        }

        const deprecatedHtml = deprecatedArticles.map(article => `
            <div class="deprecated-item">
                <div class="deprecated-header">
                    <strong>${article.title}</strong>
                    <span class="urgency-badge ${article.urgency.toLowerCase()}">${article.urgency} PRIORITY</span>
                </div>
                <div class="deprecated-features">
                    ${article.deprecated_features.map(feature => `
                        <div class="deprecated-feature">
                            <span class="feature-name">${feature.feature.toUpperCase()}</span>
                            <span class="deprecated-date">Deprecated: ${feature.deprecated_date}</span>
                            <div class="deprecation-reason">${feature.reason}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `).join('');

        return `
            <div class="section-container">
                <h4>🚨 Deprecated Content (${deprecatedArticles.length})</h4>
                <div class="deprecated-list">
                    ${deprecatedHtml}
                </div>
            </div>
        `;
    }

    renderRelevanceScores(relevanceScores) {
        console.log('Rendering relevance scores:', relevanceScores?.length || 0);
        if (!relevanceScores || relevanceScores.length === 0) {
            return '';
        }

        // Show only articles that need attention (relevance < 0.8)
        const needsAttention = relevanceScores.filter(article => article.relevance_score < 0.8);

        if (needsAttention.length === 0) {
            return `
                <div class="section-container">
                    <h4>✅ Article Relevance</h4>
                    <div class="all-current">All articles appear to be current and relevant!</div>
                </div>
            `;
        }

        const relevanceHtml = needsAttention.map(article => `
            <div class="relevance-item ${article.relevance_score < 0.3 ? 'critical' : article.relevance_score < 0.6 ? 'warning' : 'info'}">
                <div class="relevance-header">
                    <strong>${article.title}</strong>
                    <div class="relevance-score">
                        <div class="score-bar">
                            <div class="score-fill" style="width: ${article.relevance_score * 100}%"></div>
                        </div>
                        <span class="score-text">${(article.relevance_score * 100).toFixed(0)}%</span>
                    </div>
                </div>
                <div class="article-details">
                    <div class="detail-item">Author: ${article.author || 'Unknown'}</div>
                    <div class="detail-item">Version: ${article.version || 'N/A'}</div>
                    <div class="detail-item">Last Updated: ${new Date(article.last_updated).toLocaleDateString()}</div>
                </div>
                ${article.deprecated_items.length > 0 ? `
                    <div class="deprecated-in-article">
                        <strong>Contains deprecated features:</strong>
                        ${article.deprecated_items.map(item => `<span class="deprecated-tag">${item.feature}</span>`).join('')}
                    </div>
                ` : ''}
                <div class="relevance-recommendation">
                    <strong>${article.recommendation}</strong>
                </div>
            </div>
        `).join('');

        return `
            <div class="section-container">
                <h4>📅 Article Relevance Analysis (${needsAttention.length} need attention)</h4>
                <div class="relevance-list">
                    ${relevanceHtml}
                </div>
            </div>
        `;
    }

    displayError(message) {
        console.log('Displaying error:', message);
        const resultsContainer = document.getElementById('conflict-results');
        if (resultsContainer) {
            resultsContainer.innerHTML = `
                <div class="error-message">
                    <h3>❌ Error Detecting Conflicts</h3>
                    <p>${message}</p>
                    <button onclick="conflictDetector.detectConflicts()" class="retry-button">
                        🔄 Retry Analysis
                    </button>
                </div>
            `;
        }
    }
}

// Initialize the conflict detector
const conflictDetector = new ConflictDetector();
console.log('ConflictDetector script loaded'); 