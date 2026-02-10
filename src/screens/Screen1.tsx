import PasswordGate from '../components/PasswordGate';

interface Screen1Props {
  onSuccess: () => void;
}

export default function Screen1({ onSuccess }: Screen1Props) {
  return (
    <PasswordGate
      onSuccess={onSuccess}
      correctPassword="7300"
      title="Enter password"
    />
  );
}
