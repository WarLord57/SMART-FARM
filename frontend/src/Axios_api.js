import axios from 'axios';

// Create an instance of axios with base url
//use the base url of the server running in backend folder
const Axios_api = axios.create({
  baseURL: "http://192.168.8.19:8000",
});

//Export the axios instance


export default Axios_api