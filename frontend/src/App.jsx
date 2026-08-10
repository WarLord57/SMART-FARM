import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import Sensor_section from './Components/Sensor_section/Sensor_section'
import Sensor_gauge from './Components/Sensor_gauge/Sensor_gauge'
import Sensor_gauge_live from './Components/Sensorgauge_live/Sensor_gauge_live'
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  

  return (
    <>
      <div>
        <Sensor_gauge_live/>
       <Sensor_gauge/>
       <Sensor_section/>
      </div>
      
    </>
  )
}

export default App
