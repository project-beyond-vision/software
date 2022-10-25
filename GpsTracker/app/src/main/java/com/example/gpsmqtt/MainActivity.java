package com.example.gpsmqtt;

import android.content.Context;
import android.os.Build;
import android.os.Bundle;

import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;
import android.content.pm.PackageManager;
import androidx.core.app.ActivityCompat;
import android.Manifest;
import androidx.annotation.NonNull;
import android.util.Log;

import android.widget.TextView;
import android.widget.Toast;

import org.eclipse.paho.client.mqttv3.IMqttActionListener;
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.IMqttToken;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.android.service.MqttAndroidClient;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;

public class MainActivity extends AppCompatActivity {

    String clientId = MqttClient.generateClientId();
    final String subscriptionTopic = "group_05/gps_signal";
    final String publisherTopic = "group_05/gps";
    TextView statusText;
    String display;
    int duration = Toast.LENGTH_LONG;
    Context context;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        MqttAndroidClient client = new MqttAndroidClient(this.getApplicationContext(), "tcp://10.0.2.2:1883", clientId, new MemoryPersistence());

        try {
            IMqttToken token = client.connect();
            token.setActionCallback(new IMqttActionListener() {
                @Override
                public void onSuccess(IMqttToken asyncActionToken) {
                    Toast.makeText(MainActivity.this,"connected!!",Toast.LENGTH_LONG).show();
                    statusText = findViewById(R.id.statusText);
                    statusText.setText("connected"); //set text for text view
                    try{
                        client.subscribe(subscriptionTopic,0);

                    }catch (MqttException e){
                        e.printStackTrace();
                    }
                }

                @Override
                public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
                    Toast.makeText(MainActivity.this,"connection failed!!",Toast.LENGTH_LONG).show();
                }
            });

            client.setCallback(new MqttCallback() {
                @Override
                public void connectionLost(Throwable cause) {
                    statusText.setText("connection lost");
                    display = "connectionLost";
                    Log.d("connectionLost", "connectionLost");
                }

                @Override
                public void messageArrived(String topic, MqttMessage message) throws Exception {
                    String payload = new String(message.getPayload());
                    Log.d("Payload", payload);
                    statusText.setText(payload);
                    publishMessage(client, payload);
//                    Toast.makeText(context, payload, duration).show();
                }

                @Override
                public void deliveryComplete(IMqttDeliveryToken token) {

                }

            });

        } catch (MqttException e) {
            e.printStackTrace();
        }

//        checkLocationPermissions();
    }

    public void publishMessage(MqttAndroidClient client, String payload) {
        try {
            if (!client.isConnected()) {
                client.connect();
            }

            String message = payload;
            IMqttToken token = client.publish(publisherTopic, message.getBytes(), 0, false);
            token.setActionCallback( new IMqttActionListener() {
                @Override
                public void onSuccess(IMqttToken asyncActionToken) {
                    Log.i("pub success", "publish succeed!");
                }

                @Override
                public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
                    Log.i("pub fail", "publish failed!");
                }
            });
        } catch (MqttException e) {
            Log.e("error", e.toString());
            e.printStackTrace();
        }
    }

    public void checkLocationPermissions() {
        //if we have permission to access to gps location
        if (ContextCompat.checkSelfPermission(this,
                android.Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED &&
                ContextCompat.checkSelfPermission(this,
                        android.Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED) {
            //start location service
            startLocationService();
        } else {
            //If do not have location access then request permissions
            ActivityCompat.requestPermissions(this, new String[]{
                    Manifest.permission.ACCESS_FINE_LOCATION,
                    Manifest.permission.ACCESS_COARSE_LOCATION}, 1);
        }
    }

    @RequiresApi(api = Build.VERSION_CODES.M)
    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        Log.i("CODE", String.valueOf(requestCode));
        for (String p : permissions)
            Log.i("PERMISSIONS", String.valueOf(p));
        for (int g : grantResults)
            Log.i("RESULTS", String.valueOf(g));
        boolean granted = false;
        if (requestCode == 1) {
            //For each permission requested
            for (int i = 0, len = permissions.length; i < len; i++) {
                String permission = permissions[i];
                // If user denied the permission
                if (grantResults[i] == PackageManager.PERMISSION_DENIED) {
                    //Check if you asked for the same permissions before
                    boolean showRationale = shouldShowRequestPermissionRationale(permission);
                    //If user cheked "nevers ask again"
                    if (!showRationale) {
                        statusText = (TextView) findViewById(R.id.statusText);
                        statusText.setText("No access to GPS");
                    }
                    //If user hasn't checked for "never ask again"
                    else checkLocationPermissions();
                }
                //user grants permissions
                else granted = true;
            }
            //If user grants permissions
            if (granted) startLocationService();

        }
    }

    private void startLocationService() {

    }

}