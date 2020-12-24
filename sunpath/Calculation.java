import java.util.*;

/**
 * Program for calculating the sun's position (azimuth and altitude)
 * depending on the observer's local time and position (latitude + longitude)  
 * @author Jonas Schumacher
 *
 */
public class Calculation {

	/**
	 * Remarks at the beginning: 
	 * In every time zone, the sun should [in theory] be highest at 12 noon (winter time in the northern hemisphere)
	 * For CET time zone, Prague is a good example for the "center" of that time zone 
	 * 		ALTHOUGH: due to the equation of time, the "highest sun" at 12 noon oscillates roughly between Munich and Bratislava
	 * So the more you go west or east (in the same time zone), the later or earlier everything will happen 
	 */
	
	/*
	 * Variable declaration
	 */
	private Calendar myCalendar;
	private TimeZone myTimeZone;
	private TimeZone utcTimeZone;
	
	private int year;
	private int month;
	private int day;
	private int hour;
	private int minute;
	private int second;
	
	private double[][] resultTable;
	private double azimuth;
	private double altitude;
	private double latitude;
	private double longitude;
	
	private boolean sun_never_rises;
	private boolean sun_never_sets;
	
	private int sun_rise;
	private int sun_min;
	private int sun_max;
	private int sun_set;
	
/**
 * Constructor = everything is calculated by instantiating the class 'Calculation'
 * @param lat
 * @param lon
 * @param day
 * @param month
 * @param year
 */
	public Calculation(double lat, double lon, int day, int month, int year) {
		
		this.latitude = lat;
		this.longitude = lon;
		this.day = day;
		this.month = month;
		this.year = year;
		
		/*
		 * Create local calendar and extract its timezone
		 */
		/**
		 * @todo: extract time zone from coordinates instead of Calendar (now it always takes the computer's time zone) 
		 */
		
		myCalendar = Calendar.getInstance();
		myTimeZone = myCalendar.getTimeZone();
		utcTimeZone = TimeZone.getTimeZone("UTC");
		
		/*
		 * Manipulate calendar by setting time to 00h:00m:00s
		 */
		myCalendar.set(Calendar.HOUR_OF_DAY,0);
		myCalendar.set(Calendar.MINUTE,0);
		myCalendar.set(Calendar.SECOND,0);
	
		/*
		 * Set a specific day and month of the year
		 */
		myCalendar.set(Calendar.DAY_OF_MONTH,day);
		myCalendar.set(Calendar.MONTH,month-1);				// January = 01
		myCalendar.set(Calendar.YEAR,year);
		
		/*
		 * Caution: here I need to call a (.get)-method on calendar to update the calendar
		 * Otherwise, by changing the time zone later, I would start my calculations with 00:00 UTC
		 * But indeed, I want to start at 00:00 of the specific time zone (e.g. 22:00p.m. UTC [for CEST] or 23:00 UTC[for CET])
		 */
		myCalendar.get(Calendar.HOUR_OF_DAY);
		
		resultTable = new double[24*60][3];
		azimuth = 0.0;
		altitude = 0.0;
		
		/*
		 * Iterate over all minutes of a day and calculate the according azimuth & altitude
		 */
		for (int i = 0; i < resultTable.length; i++) {
			
			/*
			 * Convert calendar to UTC time for calculation:
			 */
			myCalendar.setTimeZone(utcTimeZone);
			
			year = myCalendar.get(Calendar.YEAR);
			month = myCalendar.get(Calendar.MONTH) + 1;
			day = myCalendar.get(Calendar.DAY_OF_MONTH);
			hour = myCalendar.get(Calendar.HOUR_OF_DAY);
			minute = myCalendar.get(Calendar.MINUTE);
			second = myCalendar.get(Calendar.MINUTE);
			
			Position ergebnis = getAngles(year, month, day, hour, minute, second, latitude, longitude);
			azimuth = ergebnis.getAzimuth();
			altitude = ergebnis.getAltitude();
			
			/*
			 * Convert back to local time
			 */
			myCalendar.setTimeZone(myTimeZone);
			hour = myCalendar.get(Calendar.HOUR_OF_DAY);
			minute = myCalendar.get(Calendar.MINUTE);	
			
			resultTable[i][0] = (double)hour + (double)minute/60;
			resultTable[i][1] = azimuth;
			resultTable[i][2] = altitude;
			
			myCalendar.add(Calendar.MINUTE,1);
		} // end for loop
		
		/*
		 * Calculate sunrise, sunset and highest position
		 */
		sun_never_rises = true;
		sun_never_sets = true;
		sun_max = 0;
		sun_min = 0;
		
		/*
		 * Get highest and lowest altitude
		 */
		for (int i = 0; i < resultTable.length; i++) {
			if (resultTable[i][2] >= resultTable[sun_max][2]) {
				sun_max = i;
			}
			if (resultTable[i][2] <= resultTable[sun_min][2]) {
				sun_min = i;
			}
		}
		if (resultTable[sun_max][2] > 0) {
			sun_never_rises = false;
		}
		if (resultTable[sun_min][2] < 0) {
			sun_never_sets = false;
		}		
		
		/*
		 * Only search for sunrise and sunset, if both actually happen
		 */
		if (!sun_never_rises && !sun_never_sets) {
			for (int i = 0; i < resultTable.length; i++) {
				if (resultTable[i][2] > 0) {
					sun_rise = i;
					i = resultTable.length;
				}
			}
			for (int i = sun_rise; i < resultTable.length; i++) {
				if (resultTable[i][2] < 0) {
					sun_set = i;
					i = resultTable.length;
				}
			}
		}

	}
	
/**
 * Calculate azimuth and altitude from time (in UTC) and place (coordinates)
 * @param year
 * @param month
 * @param day
 * @param hour
 * @param minute
 * @param second
 * @param latitude
 * @param longitude
 * @return
 */
	private Position getAngles(int year, int month, int day, int hour, int minute, int second, double latitude, double longitude) {

		double JDN = (1461 * (year + 4800 + (month - 14)/12))/4 + (367 * (month - 2 - 12 * ((month - 14)/12)))/12 - (3 * ((year + 4900 + (month - 14)/12)/100))/4 + day - 32075;
		//System.out.println("JDN = " + JDN);
		
		double JD = JDN + (double)(hour-12)/24 + (double)minute/1440 + (double)second/86400;
		//System.out.println("JD = " + JD);
		
		double JD0 = JDN + (double)(0-12)/24;
		//System.out.println("JD0 = " + JD0);
		
		double n = JD - 2451545;
		//System.out.println("n = " + n);
		
		// mittlere ekliptikale Länge L der Sonne
		//0.9856474 = 360/365,2422 = Winkelgeschwindigkeit der Sonne
		double L = (280.46 + 0.9856474*n)%360;
		//System.out.println("L = " + L);
		
		// mittlere Anomalie g (durch Ellipsenform)
		//0.9856003 = 360/365,2596
		double g = (357.528 + 0.9856003*n)%360;
		//System.out.println("g = " + g);	
		
		// Ekliptikale  Länge Lambda der Sonne
		// ACHTUNG: Die Winkel  müssen zuerst in Bogenmaß umgerechnet werden
		double lambda = L + 1.915*Math.sin(Math.toRadians(g))+0.01997*Math.sin(2*Math.toRadians(g));
		//System.out.println("Lambda = " + lambda);
		
		// Ekliptik
		double epsilon = 23.439 - 0.0000004*n;
		//System.out.println("Ekliptik epsilon = " + epsilon);	
		
		// Rektaszension alpha
		double alpha = 0;
		if (Math.cos(Math.toRadians(lambda)) > 0) {
			alpha = Math.toDegrees(Math.atan(Math.cos(Math.toRadians(epsilon))*Math.tan(Math.toRadians(lambda))));
		}
		else {
			alpha = Math.toDegrees(Math.atan(Math.cos(Math.toRadians(epsilon))*Math.tan(Math.toRadians(lambda)))) + 4*Math.toDegrees(Math.atan(1));
		}
		//System.out.println("Rektaszension alpha = " + alpha);	

		// Deklination delta
		double delta = 0;
		delta = Math.toDegrees(Math.asin(Math.sin(Math.toRadians(epsilon))*Math.sin(Math.toRadians(lambda))));
		//System.out.println("Deklination delta = " + delta);
		
		double T0 = (JD0 - 2451545)/36525;
		//System.out.println("Zeitpunkt T0 = " + T0);

		double T = (double)hour+(double)minute/60+(double)second/3600;
		//System.out.println("Zeitpunkt T = " + T);
		
		double sternzeit = (6.697376+2400.05134*T0+1.002738*T)%24;
		//System.out.println("Sternzeit = " + sternzeit);
		
		double stundenwinkel_greenwich = 15*sternzeit;
		//System.out.println("Stundenwinkel Frühlingspunkt Greenwich = " + stundenwinkel_greenwich);
		
		double stundenwinkel_fruehlingspunkt = stundenwinkel_greenwich + longitude;
		//System.out.println("Stundenwinkel Frühlingspunkt = " + stundenwinkel_fruehlingspunkt);
		
		double tau = stundenwinkel_fruehlingspunkt - alpha;
		//System.out.println("Tau = Stundenwinkel Sonne = " + tau);
		
		/*
		 * Azimuth and Altitude
		 * azimuth: hier muss ich erstmal die Nachtstunden (Nenner negativ) + 180° rechnen - dann hab ich eine Skala von -90 (kurz nach Sonnenaufgang) rechtsrum bis +270 (kurz vor Sonnenaufgang)
		 * dann ziehe ich 360° vor Sonnenaufgang ab und bekomme die Skala von -180 bis +180
		 */
		
		double numerator = Math.sin(Math.toRadians(tau));
		double denominator = Math.cos(Math.toRadians(tau))*Math.sin(Math.toRadians(latitude))-Math.tan(Math.toRadians(delta))*Math.cos(Math.toRadians(latitude));
		double azimuth = Math.toDegrees(Math.atan(numerator/denominator));;
		if (denominator < 0) {
			azimuth = azimuth + 180;
			if (numerator < 0) {
				azimuth = azimuth - 360;
			}
		}
		
		double termA = Math.cos(Math.toRadians(delta))*Math.cos(Math.toRadians(tau))*Math.cos(Math.toRadians(latitude));
		double termB = Math.sin(Math.toRadians(delta))*Math.sin(Math.toRadians(latitude));
		double altitude = Math.toDegrees(Math.asin(termA + termB));
		
		Position result = new Position(azimuth,altitude);
		return result;
	}
	
	/**
	 * Convert Integer hour + minute to String
	 * @param hour
	 * @param minute
	 * @return
	 */
	private String getTime(int hour, int minute) {
		String result = String.format("%02d", hour) + ":" + String.format("%02d", minute);
		return result;
	}
	
	/**
	 * Rounding function
	 * @param value
	 * @param places
	 * @return
	 */
	private static double round(double value, int places) {
	    double scale = Math.pow(10, places);
	    return Math.round(value * scale) / scale;
	}
	
	/**
	 * Save azimuth & altitude
	 * @author Jonas Schumacher
	 *
	 */
	private class Position {
	    private final double azimuth;
	    private final double altitude;

	    public Position(double a, double h) {
	        this.azimuth = a;
	        this.altitude = h;
	    }

	    public double getAzimuth() {
	        return azimuth;
	    }

	    public double getAltitude() {
	        return altitude;
	    }
	}
	
	/**
	 * Convert double hour input to (int hour + int minute)
	 * @author Jonas Schumacher
	 *
	 */
	private class Time {
		private double innerTime;
	    private int hour;
	    private int minute;
	    
	    public void setTime(double hourInput) {
	    	innerTime = hourInput;
	        hour = (int)innerTime;
	        minute = (int) ((int)60*(innerTime%hour));
	    }

	    public int getStunde() {
	        return hour;
	    }

	    public int getMinute() {
	        return minute;
	    }
	}	
	
	/**
	 * XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
	 * public get-Methods for calculated values
	 * XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
	 */
	public String getSunRise() {
		String result = null;
		if (sun_never_rises) {
			result = "sun doesnt rise";
		}
		else if (sun_never_sets) {
			result = "sun doesnt set";
		}
		else {
			Time myTime = new Time();
			myTime.setTime(resultTable[sun_rise][0]);
			result = getTime(myTime.getStunde(),myTime.getMinute());
		}
		return result;
	}
	public String getSunSet() {
		String result = null;
		if (sun_never_rises) {
			result = "sun doesnt rise";
		}
		else if (sun_never_sets) {
			result = "sun doesnt set";
		}
		else {
			Time myTime = new Time();
			myTime.setTime(resultTable[sun_set][0]);
			result = getTime(myTime.getStunde(),myTime.getMinute());
		}
		return result;
	}
	public String getSunMax() {
		Time myTime = new Time();
		myTime.setTime(resultTable[sun_max][0]);
		return getTime(myTime.getStunde(),myTime.getMinute());
	}
	public String getAzimuthRise() {
		String result = null;
		if (sun_never_rises) {
			result = "sun doesnt rise";
		}
		else if (sun_never_sets) {
			result = "sun doesnt set";
		}
		else {
			result = "" + round(resultTable[sun_rise][1],2) + "°";
		}
		return result;
	}
	public String getAzimuthSet() {
		String result = null;
		if (sun_never_rises) {
			result = "sun doesnt rise";
		}
		else if (sun_never_sets) {
			result = "sun doesnt set";
		}
		else {
			result = "" + round(resultTable[sun_set][1],2) + "°";
		}
		return result;
	}
	public String getAltitudeMax() {
		return "" + round(resultTable[sun_max][2],2) + "°";
	}
}
