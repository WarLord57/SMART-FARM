import React, { useEffect, useState } from 'react'
import { Container } from 'react-bootstrap'

import Axios_api from '../../Axios_api.js'
import './Sensor_section.css'


const Sensor_section = () => {

  // Create a state instance to handle the change of sensor data
  const [sensor_data,setSensor_data] = useState([])


  //Fetch the data sensor data from back end to display in com,ponent
  const fetchSensor_data = async()=>{
    try{
         const response = await Axios_api.get('/api')
         console.log(JSON.parse(response.data))
         const sensor_data =JSON.parse(response.data)
         setSensor_data(sensor_data)

    }catch(error){
      console.error("Error fetching sensor_data",error)

  }
}

  //use the state effect to refresh the data on rendering
  useEffect(()=>{
    fetchSensor_data();
  },[])

  return(
    <Container>
      <div className='outer-section'>
        <h2 className='section-title'>Sensor Data</h2>
        
        <div className='sensor1-section'>
        
      <table className='table-data'>
         <thead>
  <tr>
   
    <th>Temperature</th>
    <th>Humidity</th>
    <th>Mositure</th>
    <th>Moisture %</th>
    <th>Status of Moisture</th>
    <th>Status of Water Pump</th>
    <th>Date</th>
    <th>Time</th>
    
  </tr>
 </thead>
          {sensor_data.map((data,index)=>(
            <tr key={index}>
          
           
              <td>{data.temperature}</td>
              <td>{data.humidty}</td>
               <td>{data.moisture}</td>
               <td>{data.moisture_p}</td>
                <td>{data.status_moisture}</td>
                <td>{data.component1}</td>
                <td>{data.datestamp}</td>
                <td>{data.timestamp}</td>
            </tr>
          ))}
    
         </table>
        </div>
      

      </div>
    </Container>
  );
  }
  export default Sensor_section;
