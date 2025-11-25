require('@testing-library/jest-dom');
const React = require('react');
const { render, screen, within } = require('@testing-library/react');
const DashboardPage = require('@site/src/pages/dashboard/index').default;
const EvidenceFeedPage = require('@site/src/pages/dashboard/evidence').default;

describe('Analyst Dashboard route', () => {
  it('renders deterministic summary sections', () => {
    render(React.createElement(DashboardPage));

    expect(screen.getByTestId('dashboard-responsive-wrapper')).toBeInTheDocument();

    expect(
      screen.getByRole('heading', { name: /Analyst Dashboard · Summary Only/i })
    ).toBeInTheDocument();

    const riskSection = screen.getByTestId('risk-baseline');
    expect(within(riskSection).getByText(/Identity & Access/i)).toBeInTheDocument();
    expect(within(riskSection).getByText(/Guard rails steady/i)).toBeInTheDocument();

    const retrievalSection = screen.getByTestId('retrieval-spotchecks');
    expect(within(retrievalSection).getByText(/RSC-147/i)).toBeInTheDocument();

    const driftSection = screen.getByTestId('drift-summaries');
    expect(within(driftSection).getByText(/Prod · Control Plane/i)).toBeInTheDocument();

    const chartsSection = screen.getByTestId('dashboard-charts');
    expect(within(chartsSection).getByRole('heading', { name: /Analyst Dashboard Visuals/i })).toBeInTheDocument();
    expect(within(chartsSection).getByText(/GuardScore Trend/i)).toBeInTheDocument();
    expect(within(chartsSection).getByText(/Evidence Volume/i)).toBeInTheDocument();
  });
});

describe('Analyst Evidence Feed route', () => {
  it('renders the placeholder evidence feed payloads', () => {
    render(React.createElement(EvidenceFeedPage));

    expect(
      screen.getByRole('heading', { name: /Analyst Evidence Feed · Placeholder/i })
    ).toBeInTheDocument();

    const feed = screen.getByTestId('evidence-feed');
    expect(within(feed).getByText(/Vectorguard drift snapshot/i)).toBeInTheDocument();
    expect(within(feed).getByText(/vectorguard-control-plane/i)).toBeInTheDocument();
  });
});
