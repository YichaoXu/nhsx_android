package uclsse.comp0102.nhsxapp.api.extension

import android.util.Log

fun exceptionToFlase(task:()->Unit): Boolean = try{
    run(task)
    true
} catch (e: Exception){
    e.printStackTrace()
    Log.d("RunWithOutException", e.message ?: "UNKNOWN")
    false
}

