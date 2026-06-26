import { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import Background from './components/Background';
import Header from './components/Header';
import Tabs from './components/Tabs';
import LiveAdvisor from './components/LiveAdvisor';
import FleetManager from './components/FleetManager';
import EmpireBuilder from './components/EmpireBuilder';
import { useAdvice } from './hooks/useAdvice';
import { useCampaigns } from './hooks/useCampaigns';
import { useFleet } from './hooks/useFleet';
import { useBuilds } from './hooks/useBuilds';
import { applyEmpireTheme } from './theme';
import { tabSwitchVariant, usePrefersReducedMotion } from './motion';
import './App.css';

export default function App() {
  const [active, setActive] = useState('live');
  const [goal, setGoal] = useState(null);
  const [advice, setAdvice] = useAdvice();
  const { campaigns, selected, select } = useCampaigns();
  const fleet = useFleet(active === 'fleet');
  const builds = useBuilds(active === 'builder', goal);
  const reduced = usePrefersReducedMotion();

  useEffect(() => {
    if (advice?.ok) applyEmpireTheme(advice.player?.identity);
  }, [advice]);

  async function handleSelect(campaign) {
    const fresh = await select(campaign);
    setAdvice(fresh);
  }

  const variant = tabSwitchVariant(reduced);

  return (
    <>
      <Background />
      <Header advice={advice} campaigns={campaigns} selected={selected} onSelect={handleSelect} />
      <Tabs active={active} onChange={setActive} />
      <main className="view">
        <AnimatePresence mode="wait">
          <motion.div
            key={active}
            initial={variant.initial}
            animate={variant.animate}
            exit={variant.exit}
          >
            {active === 'live' && <LiveAdvisor advice={advice} />}
            {active === 'fleet' && <FleetManager data={fleet} />}
            {active === 'builder' && <EmpireBuilder data={builds} goal={goal} onGoalChange={setGoal} />}
          </motion.div>
        </AnimatePresence>
      </main>
    </>
  );
}
