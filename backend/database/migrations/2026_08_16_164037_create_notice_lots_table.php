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
        Schema::create('notice_lots', function (Blueprint $table) {
            $table->id();
            $table->string('lot_reference', 64)->unique(); // BT-137-Lot - identifikátor lotu v rámci procedúry
            $table->string('title')->nullable();                 // DL-Title-Lot / BT-23-Lot
            $table->text('description')->nullable();             // BT-24-Lot
            $table->decimal('value', 14, 2)->nullable();          // BT-27-Lot_value
            $table->char('currency', 3)->nullable();
            $table->string('main_cpv', 10)->nullable();           // BT-262-Lot
            $table->string('nuts_code', 10)->nullable();          // BT-5071-Procedure (over presný kód pre Lot level)
            $table->string('award_criterion', 32)->nullable();    // BT-539-Lot
            $table->timestamps();
            $table->jsonb('extra_fields')->nullable();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('notice_lots');
    }
};
