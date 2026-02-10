import { useState, useEffect } from 'react';
import Screen1 from './screens/Screen1';
import Screen2 from './screens/Screen2';
import Screen3 from './screens/Screen3';
import Screen4 from './screens/Screen4';
import ScreenNoReg from './screens/ScreenNoReg';
import ScreenNoDep from './screens/ScreenNoDep';

type ScreenType = 1 | 2 | 3 | 4 | 'noreg' | 'nodep';

function App() {
  const [currentScreen, setCurrentScreen] = useState<ScreenType>(1);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const screen = params.get('screen');

    if (screen === 'noreg') {
      setCurrentScreen('noreg');
    } else if (screen === 'nodep') {
      setCurrentScreen('nodep');
    }
  }, []);

  const handleScreen1Success = () => {
    setCurrentScreen(2);
  };

  const handleScreen2PrecisionUpgradeClick = () => {
    setCurrentScreen(3);
  };

  const handleScreen3PasswordSuccess = () => {
    setCurrentScreen(4);
  };

  const handleScreen3ModalClose = () => {
    setCurrentScreen(2);
  };

  return (
    <>
      {currentScreen === 1 && <Screen1 onSuccess={handleScreen1Success} />}
      {currentScreen === 2 && <Screen2 onPrecisionUpgradeClick={handleScreen2PrecisionUpgradeClick} />}
      {currentScreen === 3 && <Screen3 onPasswordSuccess={handleScreen3PasswordSuccess} onModalClose={handleScreen3ModalClose} />}
      {currentScreen === 4 && <Screen4 />}
      {currentScreen === 'noreg' && <ScreenNoReg />}
      {currentScreen === 'nodep' && <ScreenNoDep />}
    </>
  );
}

export default App;
