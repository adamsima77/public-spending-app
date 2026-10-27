<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::table('notice_lots', function (Blueprint $table) {
            $table->foreign('nuts_code')->references('code')->on('nut_codes')->nullOnDelete();
            $table->index('nuts_code');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('notice_lots', function (Blueprint $table) {
            $table->dropForeign(['nuts_code']);
            $table->dropIndex(['nuts_code']);
        });
    }
};
