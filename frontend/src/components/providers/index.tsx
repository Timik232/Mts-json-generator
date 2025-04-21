'use client';
import Style from './providers.module.scss';
import Header from '@/components/header';
import classNames from 'classnames';
import { Suspense, useLayoutEffect } from 'react';
import Blocks from '@/components/blocks';
import useTheme from '@/hooks/useTheme';

export default function Providers() {
  return (
    <Suspense fallback={<div className={Style.Providers} />}>
      <ProvidersContent />
    </Suspense>
  );
}

function ProvidersContent() {
  const { setTheme, activeTheme } = useTheme();

  useLayoutEffect(() => {
    setTheme('light');
    console.log(activeTheme);
  }, []);

  return (
    <div className={classNames(Style.Providers)}>
      <Header />
      <Blocks />
    </div>
  );
}
