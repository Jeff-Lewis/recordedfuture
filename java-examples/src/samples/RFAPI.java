package samples;

import java.io.*;

import com.sun.jersey.api.client.WebResource;
import com.sun.jersey.api.client.Client;
import com.sun.jersey.core.util.MultivaluedMapImpl;
import org.json.simple.JSONValue;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;

/**
 * 
 * Dependencies:
 * 
 * JSON Simple:
 * http://code.google.com/p/json-simple/
 * 
 * Jersey Client and Core API:
 * http://jersey.java.net/
 * 
 * A singleton class to access the Recorded Future API containing some basic methods
 * to perform aggregate entity queries
 * 
 * @author 
 *
 */
public class RFAPI {

	
	/**
	 *  Private constructor for a singleton class
	 */
	private static RFAPI rfApi = null;
	
	/**
	 * Use this method rather than a constructor to ensure that only single instance of the API is created
	 * 
	 */
	public static RFAPI getInstance() {
		 if (rfApi == null) {
			 rfApi = new RFAPI();
		 }
		 return rfApi;
	}
	
	
	/**
	 * An overloaded method that fetches aggregate results for a given entity id defined
	 * in the query file. Returns the results as a string
	 * 
	 */
	public String getAggregatesForEntity() {
		String results = null;
		try {
			Client client = Client.create();
			MultivaluedMapImpl queryParams = new MultivaluedMapImpl();
			// read the query from file
			String q = this.readQueryFromFile(RFConfig.BASEDIR + RFConfig.QUERYFILE);
			queryParams.add("q", q);
			WebResource webResource = client.resource(RFConfig.RFURL);
			String jsonResponse = webResource.queryParams(queryParams).get(String.class);
			results = this.getAggregateResults(jsonResponse);
		} catch (Exception e) {
			e.printStackTrace();
		}
		return results;
	}
	
	/**
	 * An overloaded method that takes the entity Id as a parameter and
	 * overrides the entity Id defined in the query file
	 * 
	 */
	public String getAggregatesForEntity(Integer id) {
		String results = null;;
		try {
			Client client = Client.create();
			MultivaluedMapImpl queryParams = new MultivaluedMapImpl();
			// read the query from file
			String q = this.readQueryFromFile(RFConfig.BASEDIR + RFConfig.QUERYFILE);
			JSONObject jsonObj = (JSONObject) JSONValue.parse(q);
			JSONObject queryObj = (JSONObject) jsonObj.get("aggregate_raw");
			JSONObject entityObj = (JSONObject) queryObj.get("entity");
			// set the entity Id in the query
			entityObj.put("id", id);
			String modQuery = jsonObj.toJSONString();
			queryParams.add("q", modQuery);
			WebResource webResource = client.resource(RFConfig.RFURL);
			String jsonResponse = webResource.queryParams(queryParams).get(String.class);
			results = this.getAggregateResults(jsonResponse);

		} catch (Exception e) {
			e.printStackTrace();
		}
		return results;
	}
	

	
	/**
	 * Reads a JSON query from a specified file into a string
	 */
	public String readQueryFromFile(String fileName) {

		StringBuffer sb = new StringBuffer();
		String str = null;
		try { 
			BufferedReader in = new BufferedReader(new FileReader(fileName)); 
			while ((str = in.readLine()) != null) { 
				sb.append( str );
			}
		} catch (IOException e) 
		{ 
			e.printStackTrace();
		} 
		return sb.toString();
	}


	/**
	 *  Using the Simple JSON API, decode the aggregate results and return 
	 *  as a string
	 * 
	 */
	public String getAggregateResults(String jsonText) {

		JSONParser parser=new JSONParser();
		Object obj = null; 
		String aggr =  null;
		  try {
		  obj =  parser.parse(jsonText);
		  JSONObject jsonobj = (JSONObject)obj;
		  aggr = (String) jsonobj.get("aggregates");
		                
		  } catch (Exception e) {
			  e.printStackTrace();
		  }
		  return aggr;
	}
}
