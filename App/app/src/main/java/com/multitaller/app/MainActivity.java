package com.multitaller.app;

import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import androidx.appcompat.app.AppCompatActivity;

/**
 * Actividad principal de MultiTaller
 * Esta actividad carga la aplicación web Flask en un WebView
 */
public class MainActivity extends AppCompatActivity {

    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Inicializar WebView
        webView = findViewById(R.id.webview);

        // Configurar WebViewClient para que las URLs se carguen dentro del WebView
        webView.setWebViewClient(new WebViewClient());

        // Obtener configuración del WebView
        WebSettings webSettings = webView.getSettings();

        // Habilitar JavaScript (necesario para Bootstrap y otras funcionalidades)
        webSettings.setJavaScriptEnabled(true);

        // Habilitar almacenamiento local
        webSettings.setDomStorageEnabled(true);

        // Configurar viewport
        webSettings.setLoadWithOverviewMode(true);
        webSettings.setUseWideViewPort(true);

        // Habilitar zoom
        webSettings.setSupportZoom(true);
        webSettings.setBuiltInZoomControls(true);
        webSettings.setDisplayZoomControls(false);

        // Cargar la URL de la aplicación Flask
        // NOTA: Para producción, cambia esto a la URL de tu servidor desplegado
        // Por ejemplo: https://tudominio.com o http://192.168.1.XX:5000
        webView.loadUrl("http://10.0.2.2:5000");
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
