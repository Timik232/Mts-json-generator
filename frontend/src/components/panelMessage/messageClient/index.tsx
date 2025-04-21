'use client';
import Style from './messageClient.module.scss';
import { motion } from 'framer-motion';

interface Props {
  text: string;
}

export default function MessageClient({ text }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.7 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0 }}
      transition={{
        type: 'spring',
        stiffness: 300,
        damping: 20,
      }}
      className={Style.messageClient}>
      <div>
        <h4>Вы</h4>
        <p>{text}</p>
      </div>
    </motion.div>
  );
}
