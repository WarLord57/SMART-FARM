import React, { useState,useEffect } from 'react'
import './Sensor_gauge_live.css'
import Axios_api from '../../Axios_api'
import Axios_api_esp8266 from '../../Axious_api_esp8266'
import { Button ,Container,Row,Col} from 'react-bootstrap'
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend);


const Sensor_gauge_live = () => {

 const [gauge1_data,setGaugedata1] = useState([0]);
 const [gauge2_data,setGaugedata2] = useState([0]);
 const [gauge3_data,setGaugedata3] = useState([0]);
 const [gauge4_data,setGaugedata4] = useState([0]);
 const [gauge5_data,setGaugedata5] = useState([""]);
 const [gauge6_data,setGaugedata6] = useState([0]);


const[lightIndicatorsys,setLightindicatorsys] = useState([])
const[lightIndicatorcomp,setLightindicatorcomp] = useState([])
const [status,setStatus]= useState([])
const [isButtonDisabled, setIsButtonDisabled] = useState([]);
const [isButtonText, setIsButtonText] = useState([]);
const [isPumpStatus, setPumpStatus] = useState([]);


 const fetchGaugelive = async ()=>{
    try{
      setStatus("Fetching data live data.....")
      // setLightindicatorsys(!lightIndicatorsys);
      // setLightindicatorcomp(!lightIndicatorcomp);

      const response =await Axios_api.get('/svc/api/livefeed/');

      console.log(response.data)
      if ('message' in response.data){
      
      setStatus(response.data.message)
      setGaugedata1(0)
      setGaugedata2(0)
      setGaugedata3(0)
      setGaugedata4(0)
      setGaugedata5("")
      setGaugedata6(0)
      setLightindicatorsys(!lightIndicatorsys);
      setLightindicatorcomp(!lightIndicatorcomp);
      setPumpStatus(false)
      setStatus("System irrigation is offline")
      setIsButtonText("Off")
    }else{
      setGaugedata1(Math.floor(response.data.temperature*100)/100)
      setGaugedata2(Math.floor(response.data.humidity*100)/100)
      setGaugedata3(Math.floor(response.data.moisture*100)/100)
      setGaugedata4(Math.floor(response.data.moisture_p*100)/100)
      setGaugedata5(response.data.status)
      setGaugedata6(response.data.hours)
      setStatus("System irrigation is online")
      setLightindicatorsys(lightIndicatorsys);
      if(response.data.component==1){
        setLightindicatorcomp(true)
        setPumpStatus(true)
        setIsButtonText("On")
        setStatus("Water pump is on")
      }else{
       setLightindicatorcomp(false)
        setPumpStatus(false)
      setIsButtonText("Off")
       setStatus("Water pump is off")
      }

    }

    }catch(error){
      
      setStatus("Check console for error")
      setLightindicatorsys(!lightIndicatorsys);
      setLightindicatorcomp(!lightIndicatorcomp);
      setGaugedata1(0)
      setGaugedata2(0)
      setGaugedata3(0)
      setGaugedata4(0)
      setGaugedata5("")
      setGaugedata6(0)
    }

 }


//  Function to  control pump.
 const switchPump =  async ()=>{

 if(isPumpStatus==true){
 setPumpStatus([false])
 setStatus("Turning pump off.....")
 }else{
 setPumpStatus([true])
 setStatus("Turning pump on.....")
 }


const data = {
  auto :false,
  number:isPumpStatus
}

console.log(data)


const response = await Axios_api.post('/svc/api/switch/',data)

console.log(response.data)
if(isPumpStatus==false){
  setPumpStatus(true)
  setLightindicatorcomp(true)
  setIsButtonText("On")
  setStatus("Water pump is on")
}else{
setPumpStatus(false)
setLightindicatorcomp(false)
setIsButtonText("Off")
setStatus("Water pump is off")
}  
 }


//  Funbction to switch on auto 
const switchAuto = async (value)=> {

setStatus("communicating with pump-auto "+value)

if(value==true){

setIsButtonDisabled(true)
setStatus("pump-auto on")
setPumpStatus(true)

}else{

setIsButtonDisabled(false)
setStatus("pump-auto off")

}

const data = {
  auto :value,
  number:isPumpStatus
}

console.log(data)

const response = await Axios_api.post('/api/switch/',data)

console.log(response.data)



}

 useEffect(() => {
      fetchGaugelive(); // Fetch data immediately on component mount

      const intervalId = setInterval(fetchGaugelive, 30000); // Fetch data every 30 seconds

      return () => clearInterval(intervalId); // Clear interval on component unmount
    }, []); // 

  return (
    <Container className='gauge-section'>
        <h1>Live Feed</h1>
        
        <Row>
        <div className="control-panel">
            
           <div className={lightIndicatorsys ? 'light-indicator-on' : 'light-indicator-off'}></div>
            <label>  {status}</label>
          </div>
        </Row>
        <Row>
        <div className='status-section'>
         <div className={lightIndicatorcomp ? 'light-indicator-on' : 'light-indicator-off'}> </div>
        <label> Water-Pump</label>
         <h2><p className='status-moisture'>{gauge5_data}</p></h2>
         <label> Hours_until_watering </label>
         <h3><p className='status-water-hours'><br></br>{gauge6_data}</p></h3>

         <div className="pump-control-section">
          <label>Automated</label>
          <input className='check-pump-control' type="checkbox" name='ckeck'id='check' defaultChecked={true} onClick={(e)=>switchAuto(e.target.checked)}/>
         
        <Col><Button className={isPumpStatus?'pump-button-on':'pump-button-off'} onClick={(e)=>switchPump()} disabled={isButtonDisabled}>{isButtonText}</Button></Col>
        </div>
        </div>
        </Row>
        <div className="sensor-output">
        <div className="gauge-section">
          <h2>Temperature</h2>
          <div className="gauge-inner">
            <p>{gauge1_data}</p>
          </div>
        </div>
        <div className="gauge-section">
          <h2>Humidity</h2>
          <div className="gauge-inner">
            <p>{gauge2_data}</p>
          </div>
        </div>
        <div className="gauge-section">
          <h2>Moisture</h2>
          <div className="gauge-inner">
            <p>{gauge3_data}</p>
          </div>
        </div>
        <div className="gauge-section">
          <h2>Moisture %</h2>
          <div className="gauge-inner">
            <p>{gauge4_data}</p>
          </div>
        </div>
        </div>
    </Container>
  )
}

export default Sensor_gauge_live