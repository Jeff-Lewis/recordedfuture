package samples;

/**
 * Simple test class to test sample 
 * 
 * @author 
 *
 */
public class RFAPITest {
	

	public static void main(String[] args) {
		RFAPITest test = new RFAPITest();
		test.testGettAggregatesForEntity();
		test.testGettAggregatesForEntity(33334336);	
	}
	
	void testGettAggregatesForEntity(){
		String results = RFAPI.getInstance().getAggregatesForEntity();
		System.out.println("results: " + results);
	}
	
	void testGettAggregatesForEntity(int id){
		String results = RFAPI.getInstance().getAggregatesForEntity(id);
		System.out.println("results for entityId: " + id +": " + results);
	}


}
