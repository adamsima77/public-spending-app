<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('downloaded_files', function (Blueprint $table) {
            $table->id();
            $table->string('file_id')->unique();       // Extrahované ID z URL (napr. '12345')
            $table->text('url');                       // Plná URL adresa na stiahnutie
            $table->string('filename')->nullable();     // Názov uloženého súboru na disku
            $table->timestamp('downloaded_at')->nullable();
            $table->timestamp('parsed_at')->nullable();
            $table->string('file_hash', 64)->nullable()->index();
            $table->string('format', 255)->nullable()->after('filename');
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('downloaded_files');
    }
};