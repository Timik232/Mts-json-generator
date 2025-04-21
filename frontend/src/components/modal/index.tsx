'use client';
import { useState, useEffect, ReactNode } from 'react';
import { createPortal } from 'react-dom';
import Style from './modal.module.scss';
import { AnimatePresence, motion } from 'framer-motion';

type ModalProps = {
  isOpen: boolean;
  onClose: () => void;
  children: ReactNode;
  heading: string;
};

const Modal = ({ isOpen, onClose, children, heading }: ModalProps) => {
  const [isBrowser, setIsBrowser] = useState(false);

  // Ждем полного монтирования в браузере
  useEffect(() => {
    setIsBrowser(true);
    return () => setIsBrowser(false);
  }, []);

  // Обработка Esc
  useEffect(() => {
    if (!isBrowser || !isOpen) return;

    const fuckOff = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    window.addEventListener('keydown', fuckOff);
    return () => window.removeEventListener('keydown', fuckOff);
  }, [isOpen, onClose, isBrowser]);

  if (!isBrowser) return null;

  return createPortal(
    <AnimatePresence mode="wait">
      {isOpen && (
        <motion.div
          key="overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className={Style.ModalOverlay}
          onClick={(e) => e.target === e.currentTarget && onClose()}
          transition={{ duration: 0.3 }}>
          <motion.div
            key="content"
            initial={{ scale: 0.7, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{
              scale: 0.7,
              opacity: 0,
              transition: {
                duration: 0.3,
                ease: 'easeInOut',
              },
            }}
            className={Style.ModalContent}
            transition={{
              type: 'spring',
              stiffness: 300,
              damping: 15,
            }}>
            <h3>{heading}</h3>
            {children}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>,
    document.body,
  );
};

export default Modal;
