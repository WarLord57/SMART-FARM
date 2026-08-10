import React, { useEffect, useState } from 'react'
import './Sensor_gauge.css'
import Axios_api from '../../Axios_api'
import { Button} from 'react-bootstrap'
import { Container } from 'react-bootstrap'
import { Modal } from 'react-bootstrap'
import { Form } from 'react-bootstrap'

const Sensor_gauge = () => {

  //Get current date
  const date = new Date();
  
  const formattedDate = date.toISOString().slice(0, 10);
  // console.log(formattedDate);  Example output: 2025-08-28



  // Create a state for the change in gauge readings
  const [gauge1_data,setGaugedata1] = useState([0]);
  const [gauge2_data,setGaugedata2] = useState([0]);
  const [gauge3_data,setGaugedata3] = useState([0]);
  const [gauge4_data,setGaugedata4] = useState([0]);

  const [start_datestamp, setStart_datestamp] = useState(formattedDate);
  const [end_datestamp, setEnd_datestamp] = useState(formattedDate);
  const [frequency, setFrequncy] = useState(0);
  const [show, setShow] = useState(false);

  const filterData = {
      start_datestamp:start_datestamp,
      end_datestamp: end_datestamp,
      frequency: frequency,
    };

   

  const fetchGauge_data = async()=>{
     console.log(filterData)
    try{
      const response = await Axios_api.post('/api/agg/',filterData)
      console.log("Fetching ....filter data")
      console.log(response.data)
    
      if (response.data.message!=null){
        setGaugedata1(response.data.message)
        setGaugedata2(response.data.message)
        setGaugedata3(response.data.message)
        setGaugedata4(response.data.message)

      }else{
        setGaugedata1(Math.round(response.data.temperature*100)/100)
        setGaugedata2(Math.round(response.data.humidty*100)/100)
        setGaugedata3(Math.round(response.data.moisture*100)/100)
        setGaugedata4(Math.round(response.data.moisture_p*100)/100)
      }
      // setGaugedata(response)


    }catch(error){
      console.error("Failed to fetch data ",error)

    }
    
  }
   

  const fetchFilter_data = ()=>{
    console.log("Updating filter")
    fetchGauge_data();
  }

  const handleClose = () =>{
    fetchFilter_data()
    setShow(false);
  }
  const handleShow = () => setShow(true);

useEffect(()=>{
  fetchGauge_data();
},
[])
  return (
    <Container className='gauge-section'>
          <hr/>
        <h1>Sensor overview</h1>
       <Modal className="input-section" show={show} onHide={handleClose}>
            <Form>
            <label>Start Date</label>
            <input type='date'name='start_date' id='start_date' value={start_datestamp} onChange={(e)=>setStart_datestamp(e.target.value)}/>
            <label>End Date</label>
            <input type='date'name='end_date'id='end_date' value={end_datestamp} onChange={(e)=>setEnd_datestamp(e.target.value)}/>
            <label>Frequency</label>
            <input type='input' id='frequency' name ='frequency' value={frequency} onChange={(e)=>setFrequncy(e.target.value)}/>
            </Form>
            <Modal.Footer>
            
            <Button variant="primary" onClick={handleClose}>
                Save Changes
            </Button>
            </Modal.Footer>
        </Modal>
         <Button variant="primary" onClick={handleShow}>
                Filter
          </Button>
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

export default Sensor_gauge