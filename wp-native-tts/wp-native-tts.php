<?php
/**
 * Plugin Name: WP Native TTS
 * Description: Un lecteur audio autonome utilisant la Web Speech API pour lire le contenu des articles.
 * Version: 1.0.0
 * Author: VELLORA PARIS
 * Text Domain: wp-native-tts
 */

if (!defined('ABSPATH')) {
    exit;
}

class WP_Native_TTS {

    public function __construct() {
        add_action('admin_menu', array($this, 'add_admin_menu'));
        add_action('admin_init', array($this, 'register_settings'));

        add_action('wp_enqueue_scripts', array($this, 'enqueue_assets'));

        add_filter('the_content', array($this, 'inject_player_into_content'));
        add_shortcode('article_audio_player', array($this, 'tts_shortcode'));
    }

    // --- Admin Settings ---

    public function add_admin_menu() {
        add_options_page(
            'Réglages WP Native TTS',
            'WP Native TTS',
            'manage_options',
            'wp-native-tts',
            array($this, 'options_page_html')
        );
    }

    public function register_settings() {
        register_setting('wp_native_tts_settings', 'wp_native_tts_language', array('default' => 'fr-FR'));
        register_setting('wp_native_tts_settings', 'wp_native_tts_rate', array('default' => 1));
        register_setting('wp_native_tts_settings', 'wp_native_tts_pitch', array('default' => 1));
        register_setting('wp_native_tts_settings', 'wp_native_tts_position', array('default' => 'before'));
        register_setting('wp_native_tts_settings', 'wp_native_tts_post_types', array(
            'default' => array('post'),
            'sanitize_callback' => array($this, 'sanitize_post_types')
        ));
    }

    public function sanitize_post_types($input) {
        if (!is_array($input) || empty($input)) {
            return array();
        }
        return array_map('sanitize_text_field', $input);
    }

    public function options_page_html() {
        if (!current_user_can('manage_options')) {
            return;
        }

        $post_types = get_post_types(array('public' => true), 'objects');
        $selected_post_types = get_option('wp_native_tts_post_types', array('post'));
        ?>
        <div class="wrap">
            <h1>Réglages WP Native TTS</h1>
            <form action="options.php" method="post">
                <?php
                settings_fields('wp_native_tts_settings');
                do_settings_sections('wp_native_tts_settings');
                ?>
                <table class="form-table">
                    <tr>
                        <th scope="row">Code Langue (ex: fr-FR, en-US)</th>
                        <td><input type="text" name="wp_native_tts_language" value="<?php echo esc_attr(get_option('wp_native_tts_language', 'fr-FR')); ?>" /></td>
                    </tr>
                    <tr>
                        <th scope="row">Vitesse de lecture (Rate) [0.1 à 10]</th>
                        <td><input type="number" step="0.1" min="0.1" max="10" name="wp_native_tts_rate" value="<?php echo esc_attr(get_option('wp_native_tts_rate', 1)); ?>" /></td>
                    </tr>
                    <tr>
                        <th scope="row">Tonalité (Pitch) [0 à 2]</th>
                        <td><input type="number" step="0.1" min="0" max="2" name="wp_native_tts_pitch" value="<?php echo esc_attr(get_option('wp_native_tts_pitch', 1)); ?>" /></td>
                    </tr>
                    <tr>
                        <th scope="row">Emplacement Automatique</th>
                        <td>
                            <select name="wp_native_tts_position">
                                <option value="before" <?php selected(get_option('wp_native_tts_position', 'before'), 'before'); ?>>Avant le contenu</option>
                                <option value="after" <?php selected(get_option('wp_native_tts_position', 'before'), 'after'); ?>>Après le contenu</option>
                                <option value="none" <?php selected(get_option('wp_native_tts_position', 'before'), 'none'); ?>>Aucun (Shortcode uniquement)</option>
                            </select>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row">Types de publication actifs</th>
                        <td>
                            <!-- Hidden input ensures an empty array is sent if all checkboxes are unchecked -->
                            <input type="hidden" name="wp_native_tts_post_types" value="">
                            <?php foreach ($post_types as $pt) : ?>
                                <label>
                                    <input type="checkbox" name="wp_native_tts_post_types[]" value="<?php echo esc_attr($pt->name); ?>" <?php checked(in_array($pt->name, $selected_post_types)); ?>>
                                    <?php echo esc_html($pt->label); ?>
                                </label><br>
                            <?php endforeach; ?>
                        </td>
                    </tr>
                </table>
                <?php submit_button(); ?>
            </form>
        </div>
        <?php
    }

    // --- Frontend Logic ---

    public function enqueue_assets() {
        $post_types = get_option('wp_native_tts_post_types', array('post'));

        if (is_singular($post_types)) {
            wp_enqueue_style('wp-native-tts-style', plugin_dir_url(__FILE__) . 'assets/tts-player.css', array(), '1.0.0');
            wp_enqueue_script('wp-native-tts-script', plugin_dir_url(__FILE__) . 'assets/tts-player.js', array(), '1.0.0', true);

            global $post;
            $clean_text = wp_strip_all_tags(strip_shortcodes($post->post_content));

            wp_localize_script('wp-native-tts-script', 'wpNativeTTSData', array(
                'text'     => $clean_text,
                'language' => get_option('wp_native_tts_language', 'fr-FR'),
                'rate'     => get_option('wp_native_tts_rate', 1),
                'pitch'    => get_option('wp_native_tts_pitch', 1),
            ));
        }
    }

    public function get_player_html() {
        return '
        <div class="wp-native-tts-player">
            <button class="tts-btn tts-play" aria-label="Lire l\'article">
                <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
            </button>
            <button class="tts-btn tts-pause" aria-label="Mettre en pause" style="display:none;">
                <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>
            </button>
            <button class="tts-btn tts-stop" aria-label="Arrêter la lecture" style="display:none;">
                <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect></svg>
            </button>
            <span class="tts-status">Écouter l\'article</span>
        </div>';
    }

    public function inject_player_into_content($content) {
        if (!is_main_query() || !in_the_loop()) {
            return $content;
        }

        $post_types = get_option('wp_native_tts_post_types', array('post'));
        if (!is_singular($post_types)) {
            return $content;
        }

        $position = get_option('wp_native_tts_position', 'before');
        $player_html = $this->get_player_html();

        if ($position === 'before') {
            return $player_html . $content;
        } elseif ($position === 'after') {
            return $content . $player_html;
        }

        return $content;
    }

    public function tts_shortcode() {
        return $this->get_player_html();
    }
}

new WP_Native_TTS();
