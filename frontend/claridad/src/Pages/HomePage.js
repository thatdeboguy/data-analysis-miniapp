import api from '../api';
import React, { useState } from 'react';
import DataTable from 'react-data-table-component';
import 'bootstrap/dist/css/bootstrap.min.css';


function HomePage() {
    const [file, setfile] = useState(null);
    const [query, setQuery] = useState('');
    const [queryResult, setQueryResult] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleFileChange = (event) => {
        setfile(event.target.files[0]);        
    }
    // Function to handle csv file upload
    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!file) {
            alert("Please select a file first!");
            return;
        }
        // if( file.type !== 'text/csv' ) {
        //     alert("Please select a CSV file!");
        //     return;
        // }
        if (!file.name.toLowerCase().endsWith('.csv')) {
        alert("Please select a CSV file!");
        return;
        }

        setIsLoading(true);
        const formData = new FormData();
        formData.append('file', file);
        try{
            const response = await api.post('/uploadfile', formData,{
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            alert("File uploaded successfully!");
            console.log(response.data);           
            
        }catch(error){
            alert(`Error uploading file: ${error.message}`);
            console.error("Error uploading file:", error);
        }finally{
            setIsLoading(false);
            setfile(null);
        }
    };
    const handleQUery = async (e) =>{
        e.preventDefault();
        if(!query){
            alert("Please enter a SQL query!");
            return;
        }
        if(!query.endsWith(';')){
            alert("SQL query should end with a semicolon (;)");
            return;
        }
        
        try{
            const response = await api.post('/sqlquery', { query }
            );
            setQueryResult(response.data);
            console.log("query columns:", response.data);
            console.log(response.data);
        }catch(error){
            alert(`Error executing query: ${error.message}`);
            console.error("Error executing query:", error);
        }
        setQuery('');
    }
    return (
    <div className="container my-5">
        {/* Upload Section */}
        <aside className="mb-5 p-4 border rounded bg-light shadow-sm">
            <h4 className="mb-3 text-primary">Upload Your CSV File</h4>
            <form onSubmit={handleSubmit} className="d-flex flex-column flex-md-row align-items-center gap-3">
                <input 
                    type="file" 
                    accept=".csv" 
                    className="form-control w-50"
                    onChange={handleFileChange} 
                />
                <button 
                    type="submit" 
                    className="btn btn-success"
                    disabled={isLoading}
                >
                    {isLoading ? (
                        <>
                            <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                            Uploading...
                        </>
                    ) : (
                        'Upload CSV'
                    )}
                </button>
            </form>
        </aside>

        {/* Query Section */}
        <section className="p-4 border rounded bg-white shadow-sm">
            <h2 className="text-center text-primary mb-3">Welcome to Claridad</h2>
            <p className="text-center text-muted mb-4">
                Your data, your insights. Upload CSV files and run SQL queries with ease.
            </p>

            {/* SQL Query Input */}
            <form onSubmit={handleQUery} className="d-flex flex-column flex-md-row align-items-center justify-content-center gap-3 mb-4">
                <input 
                    type="text" 
                    className="form-control w-75"
                    placeholder="Enter your SQL query here..." 
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                />
                <button type="submit" className="btn btn-primary">
                    Run Query
                </button>
            </form>

            {/* Query Results */}
            <div>
                {queryResult && (
                    <div className="card shadow-sm p-3">
                        <h4 className="card-title mb-3">Query Results</h4>
                        <DataTable
                            columns={queryResult.columns.map(col => ({
                                name: col,
                                selector: row => row[col],
                                sortable: true
                            }))}
                            data={queryResult.data}
                            pagination
                            highlightOnHover
                            striped
                        />
                    </div>
                )}
            </div>
        </section>
    </div>
);

}
export default HomePage;