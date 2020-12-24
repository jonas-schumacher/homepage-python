import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.MessageBox;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Text;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.events.KeyAdapter;
import org.eclipse.swt.events.KeyEvent;
import org.eclipse.swt.widgets.DateTime;
import org.eclipse.swt.custom.SashForm;
import org.eclipse.wb.swt.SWTResourceManager;

/**
 * GUI for running "Calculation" based on user input for time (calendar) and position (latitude + longitude)
 * @author Jonas Schumacher
 *
 */
public class Gui extends Composite {
	private Text lat;
	private Text lon;
	private Label result_time1;
	private Label result_time2;
	private Label result_time3;
	private Label result_angle1;
	private Label result_angle2;
	private Label result_angle3;
	private static Button btnRun;
	private DateTime dateTime;
	private Label lblSun;
	private Composite composite;
	private Label lblVerticalSpace1;
	private Label lblVerticalSpace2;
	private Label lblNewLabel_1;
	private Label lblNewLabel_2;
	
	public static void main(String[] args) {
		Display display = new Display();
		Shell shell = new Shell(display);
		shell.setLayout(new GridLayout(1, false));

		Gui myGui = new Gui(shell,SWT.NONE);
		
		shell.setDefaultButton(btnRun);
		
		shell.pack();
		shell.open();
		while (!shell.isDisposed()) {
			if (!display.readAndDispatch())
				display.sleep();
		}
		display.dispose();
	}
	
	/**
	 * Create the composite.
	 * @param parent
	 * @param style
	 */
	public Gui(Composite parent, int style) {
		super(parent, style);
		setLayout(new GridLayout(4, false));
		
		lblSun = new Label(this, SWT.NONE);
		lblSun.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, false, false, 4, 1));
		lblSun.setFont(SWTResourceManager.getFont("Segoe UI", 14, SWT.BOLD));
		lblSun.setText("Sun path calculator");
		
		Label lblInsertCoordinates = new Label(this, SWT.NONE);
		lblInsertCoordinates.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, true, false, 4, 1));
		lblInsertCoordinates.setText("Enter coordinates + date and hit \"Run!\"");
		
		/*
		 * Latitude
		 */
		
		lblNewLabel_1 = new Label(this, SWT.NONE);
		new Label(this, SWT.NONE);
		/*
		 * Calendar
		 */
		dateTime = new DateTime(this, SWT.BORDER | SWT.CALENDAR);
		dateTime.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, false, false, 2, 4));
		Label lblLongitude = new Label(this, SWT.NONE);
		GridData gd_lblLongitude = new GridData(SWT.LEFT, SWT.CENTER, false, false, 1, 1);
		gd_lblLongitude.widthHint = 54;
		lblLongitude.setLayoutData(gd_lblLongitude);
		lblLongitude.setText("Latitude");
		
		lat = new Text(this, SWT.BORDER);
		lat.setText("51.514886");
		lat.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
		
		/*
		 * Longitude
		 */
		
		lblNewLabel_2 = new Label(this, SWT.NONE);
		new Label(this, SWT.NONE);
		Label lblLongitude_1 = new Label(this, SWT.NONE);
		GridData gd_lblLongitude_1 = new GridData(SWT.LEFT, SWT.TOP, false, false, 1, 1);
		gd_lblLongitude_1.widthHint = 65;
		lblLongitude_1.setLayoutData(gd_lblLongitude_1);
		lblLongitude_1.setText("Longitude");
		
		lon = new Text(this, SWT.BORDER);
		lon.setText("7.453226");
		GridData gd_lon = new GridData(SWT.FILL, SWT.TOP, true, false, 1, 1);
		gd_lon.widthHint = 135;
		lon.setLayoutData(gd_lon);
		

		/*
		 * Run-Button
		 */

		btnRun = new Button(this, SWT.NONE);
		btnRun.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				/*
				 * Get lon and lat
				 */
				try {
					double mylat = Double.parseDouble(lat.getText());
					double mylon = Double.parseDouble(lon.getText());
					
					int day = dateTime.getDay();
					int month = dateTime.getMonth() + 1; 
					int year = dateTime.getYear();
					
					Calculation cal = new Calculation(mylat,mylon,day, month, year);
					result_time1.setText(cal.getSunRise());
					result_time2.setText(cal.getSunMax());
					result_time3.setText(cal.getSunSet());
					result_angle1.setText(cal.getAzimuthRise());
					result_angle2.setText(cal.getAltitudeMax());
					result_angle3.setText(cal.getAzimuthSet());
				}
				catch (NumberFormatException nfe) {
					MessageBox box = new MessageBox(parent.getShell());
					box.setText("Error");
					box.setMessage("Wrong coordinate format [use format XX.XXXX]");
					box.open();
				}
			}
		});
		GridData gd_btnRun = new GridData(SWT.FILL, SWT.FILL, true, false, 4, 1);
		gd_btnRun.heightHint = 52;
		btnRun.setLayoutData(gd_btnRun);
		btnRun.setText("Run!");
		
		/*
		 * Result = New Grid Layout
		 */
		composite = new Composite(this, SWT.NONE);
		composite.setLayout(new GridLayout(6, false));
		GridData gd_composite = new GridData(SWT.FILL, SWT.CENTER, true, false, 4, 1);
		gd_composite.heightHint = 67;
		composite.setLayoutData(gd_composite);
		
		// Sunrise time
		Label lblSunrise = new Label(composite, SWT.NONE);
		GridData gd_lblSunrise = new GridData(SWT.LEFT, SWT.CENTER, false, false, 1, 1);
		gd_lblSunrise.widthHint = 83;
		lblSunrise.setLayoutData(gd_lblSunrise);
		lblSunrise.setSize(61, 15);
		lblSunrise.setText("Sunrise at");
		
		result_time1 = new Label(composite, SWT.NONE);
		GridData gd_result_time1 = new GridData(SWT.FILL, SWT.CENTER, false, false, 1, 1);
		gd_result_time1.widthHint = 86;
		result_time1.setLayoutData(gd_result_time1);
		result_time1.setBackground(SWTResourceManager.getColor(SWT.COLOR_TITLE_BACKGROUND_GRADIENT));
		result_time1.setText("        ");
		result_time1.setLocation(59, 4);
		result_time1.setSize(55, 32);
		
		lblVerticalSpace1 = new Label(composite, SWT.NONE);
		GridData gd_lblNewLabel = new GridData(SWT.LEFT, SWT.CENTER, false, false, 1, 1);
		gd_lblNewLabel.widthHint = 10;
		lblVerticalSpace1.setLayoutData(gd_lblNewLabel);
		lblVerticalSpace1.setText("        ");
		
		// Sunrise angle
		Label lblAzimuth = new Label(composite, SWT.NONE);
		GridData gd_lblAzimuth = new GridData(SWT.FILL, SWT.CENTER, false, false, 1, 1);
		gd_lblAzimuth.widthHint = 126;
		lblAzimuth.setLayoutData(gd_lblAzimuth);
		lblAzimuth.setText("Azimuth at sunrise");
		
		result_angle1 = new Label(composite, SWT.NONE);
		GridData gd_result_angle1 = new GridData(SWT.FILL, SWT.CENTER, false, false, 1, 1);
		gd_result_angle1.widthHint = 87;
		result_angle1.setLayoutData(gd_result_angle1);
		result_angle1.setBackground(SWTResourceManager.getColor(SWT.COLOR_TITLE_BACKGROUND_GRADIENT));
		result_angle1.setText("        ");
		
		lblVerticalSpace2 = new Label(composite, SWT.NONE);
		GridData gd_lblFgasdf = new GridData(SWT.LEFT, SWT.CENTER, false, false, 1, 1);
		gd_lblFgasdf.widthHint = 13;
		lblVerticalSpace2.setLayoutData(gd_lblFgasdf);
		lblVerticalSpace2.setText("        ");
		
		
		// Culmination time
		Label lblSunpeak = new Label(composite, SWT.NONE);
		GridData gd_lblSunpeak = new GridData(SWT.LEFT, SWT.CENTER, false, false, 1, 1);
		gd_lblSunpeak.widthHint = 83;
		lblSunpeak.setLayoutData(gd_lblSunpeak);
		lblSunpeak.setText("Culmination at");
		
		result_time2 = new Label(composite, SWT.NONE);
		GridData gd_result_time2 = new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1);
		gd_result_time2.widthHint = 43;
		result_time2.setLayoutData(gd_result_time2);
		result_time2.setBackground(SWTResourceManager.getColor(SWT.COLOR_TITLE_BACKGROUND_GRADIENT));
		result_time2.setText("        ");
		new Label(composite, SWT.NONE);
		
		// Culmination angle
		Label lblAltitude = new Label(composite, SWT.NONE);
		lblAltitude.setText("Altitude at culmination");
		
		result_angle2 = new Label(composite, SWT.NONE);
		GridData gd_result_angle2 = new GridData(SWT.FILL, SWT.CENTER, false, false, 1, 1);
		gd_result_angle2.widthHint = 37;
		result_angle2.setLayoutData(gd_result_angle2);
		result_angle2.setBackground(SWTResourceManager.getColor(SWT.COLOR_TITLE_BACKGROUND_GRADIENT));
		result_angle2.setText("        ");
		new Label(composite, SWT.NONE);
		
		// Sunset time
		Label lblSunsetAt = new Label(composite, SWT.NONE);
		lblSunsetAt.setText("Sunset at");
		
		result_time3 = new Label(composite, SWT.NONE);
		GridData gd_result_time3 = new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1);
		gd_result_time3.widthHint = 43;
		result_time3.setLayoutData(gd_result_time3);
		result_time3.setBackground(SWTResourceManager.getColor(SWT.COLOR_TITLE_BACKGROUND_GRADIENT));
		result_time3.setText("        ");
		new Label(composite, SWT.NONE);
		
		// Sunset angle		
		Label label_4 = new Label(composite, SWT.NONE);
		label_4.setText("Azimuth at sunset");
		
		result_angle3 = new Label(composite, SWT.NONE);
		result_angle3.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false, 1, 1));
		result_angle3.setBackground(SWTResourceManager.getColor(SWT.COLOR_TITLE_BACKGROUND_GRADIENT));
		result_angle3.setText("        ");
		new Label(composite, SWT.NONE);
	}

}
